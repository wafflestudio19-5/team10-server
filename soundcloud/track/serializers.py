from rest_framework import serializers, status
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import APIException
from track.models import Track
from user.serializers import UserSerializer
from tag.serializers import TagSerializer
from reaction.serializers import LikeSerializer, RepostSerializer
from soundcloud.settings.common import *
import boto3
import re


class TrackSerializer(serializers.ModelSerializer):

    artist = UserSerializer(read_only=True)
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    likes = LikeSerializer(many=True, read_only=True)
    reposts = RepostSerializer(many=True, read_only=True)
    # comments = CommentSerializer(many=True, read_only=True)
    audio_filename = serializers.CharField(write_only=True)
    image_filename = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'description',
            'created_at',
            'count',
            'genre',
            'tags',
            'is_private',
            'like_count',
            'repost_count',
            'comment_count',
            'likes',
            'reposts',
            'audio_filename',
            'image_filename',
            # 'comments',
        )
        extra_kwargs = {
            'audio': {'read_only': True},
            'image': {'read_only': True},
            'created_at': {'read_only': True},
            'count': {'read_only': True},
        }

    def get_like_count(self, track):
        return track.likes.count()

    def get_repost_count(self, track):
        return track.reposts.count()

    def get_comment_count(self, track):
        return track.comment_set.count()

    def validate(self, data):
        user = self.context.get('request').user
        audio_filename = data.get('audio_filename')
        image_filename = data.get('image_filename')
        permalink = data.get('permalink')
        filename_pattern = re.compile('^[a-zA-Z0-9\/\!\-\_\.\*\'\(\)]+$')
        permalink_pattern = re.compile('^[a-z0-9\-\_]+$')

        detail = dict()

        if audio_filename is not None:
            if not audio_filename.lower().endswith(('.wav', '.flac', '.aiff', '.alac', 'mp3', '.aac', '.ogg', '.oga', '.mp4', '.mp2', '.m4a', '.3gp', '.3g2', '.mj2', '.amr', '.wma')):
                detail['audio_filename_extension'] = "Unsupported audio file extension."
            if not re.search(filename_pattern, audio_filename):
                detail['audio_filename_pattern'] = "Incorrect audio filename format."

        if image_filename is not None:
            if not image_filename.lower().endswith(('.jpg', '.png')):
                detail['image_filename_extension'] = "Unsupported image file extension."
            if not re.search(filename_pattern, image_filename):
                detail['image_filename_pattern'] = "Incorrect image filename format."

        if permalink is not None:
            if len(permalink) < 3 or len(permalink) > 255:
                detail['permalink_length'] = "Permalink must be at least 3 characters and at most 255 characters."
            if not any(c.isalpha() for c in permalink):
                detail['permalink_alphabet'] = "Permalink must contain at least one alphabetic character."
            if not re.search(permalink_pattern, permalink):
                detail['permalink_pattern'] = "Only lowercase letters/numbers/_/- are allowed in permalink."

        if detail:
            raise ValidationError(detail)


        # Check if the same filename (url) already exists in database.
        audio_url = S3_BASE_URL + S3_MUSIC_TRACK_DIR + audio_filename
        if Track.objects.filter(audio=audio_url).exists():
            raise FilenameConflictError("Already existing audio file name.")
        
        if image_filename is not None:
            image_url = S3_BASE_URL + S3_IMAGES_TRACK_DIR + image_filename
            if Track.objects.filter(image=image_url).exists():
                raise FilenameConflictError("Already existing image file name.")

        # Check if the same permalink already exists in database.
        if user.owned_tracks.filter(permalink=permalink).exists():
            raise PermalinkConflictError()

        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        audio_filename = validated_data.pop('audio_filename')
        image_filename = validated_data.pop('image_filename', None)
        audio_url = S3_BASE_URL + S3_MUSIC_TRACK_DIR + audio_filename
        image_url = S3_BASE_URL + S3_IMAGES_TRACK_DIR + image_filename if image_filename is not None else None

        # Update validated_data and create track object.
        validated_data.update(
            {'artist': user, 'audio': audio_url, 'image': image_url}
        )
        track = super().create(validated_data)
        data = SimpleTrackSerializer(track).data

        # Generate presigned url for audio file.
        audio_presigned_url = boto3.client(
            's3',
            region_name=S3_REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        ).generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': S3_BUCKET_NAME,
                    'Key': S3_MUSIC_TRACK_DIR + audio_filename},
            ExpiresIn=300
        )

        # Generate presigned url for image file only if image_filename exists.
        if image_filename is not None:
            image_presigned_url = boto3.client(
                's3',
                region_name=S3_REGION_NAME,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            ).generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': S3_BUCKET_NAME,
                        'Key': S3_IMAGES_TRACK_DIR + image_filename},
                ExpiresIn=300
            )
        else:
            image_presigned_url = None

        data.update(
            {'audio_presigned_url': audio_presigned_url,
                'image_presigned_url': image_presigned_url}
        )
        return data, status.HTTP_201_CREATED


class SimpleTrackSerializer(serializers.ModelSerializer):

    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'genre',
            'count',
            'like_count',
            'repost_count',
            'comment_count',
        )

    def get_like_count(self, track):
        return track.likes.count()

    def get_repost_count(self, track):
        return track.reposts.count()

    def get_comment_count(self, track):
        return track.comment_set.count()


class FilenameConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('Already existing filename.')
    default_code = 'filename_conflict'


class PermalinkConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('Already existing permalink')
    default_code = "permalink_conflict"
