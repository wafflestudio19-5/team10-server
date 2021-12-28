from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from track.models import Track
from tag.serializers import TagSerializer
from user.serializers import UserSerializer
from reaction.serializers import LikeSerializer, RepostSerializer
from django.conf import settings
from soundcloud.exceptions import ConflictError
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
            'permalink': {
                'max_length': 255,
                'min_length': 3,
            },
        }
        read_only_fields = (
            'audio',
            'image',
            'created_at',
            'count',
        )

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, track):
        return track.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, track):
        return track.reposts.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_comment_count(self, track):
        return track.comment_set.count()

    def validate_audio_filename(self, value):
        pattern = re.compile('^[a-zA-Z0-9\/\!\-\_\.\*\'\(\)]+$')

        if not value.lower().endswith(('.wav', '.flac', '.aiff', '.alac', 'mp3', '.aac', '.ogg', '.oga', '.mp4', '.mp2', '.m4a', '.3gp', '.3g2', '.mj2', '.amr', '.wma')):
            raise ValidationError("Unsupported audio file extension.")
        if not re.search(pattern, value):
            raise ValidationError("Incorrect audio filename format.")

        return value

    def validate_image_filename(self, value):
        pattern = re.compile('^[a-zA-Z0-9\/\!\-\_\.\*\'\(\)]+$')

        if not value.lower().endswith(('.jpg', '.png')):
            raise ValidationError("Unsupported image file extension.")
        if not re.search(pattern, value):
            raise ValidationError("Incorrect image filename format.")

        return value

    def validate_permalink(self, value):
        pattern = re.compile('^[a-z0-9\-\_]+$')

        if not any(c.isalpha() for c in value):
            raise ValidationError("Permalink must contain at least one alphabetic character.")
        if not re.search(pattern, value):
            raise ValidationError("Only lowercase letters/numbers/_/- are allowed in permalink.")

        return value

    def validate(self, data):
        audio_filename = data.pop('audio_filename', None)
        image_filename = data.pop('image_filename', None)
        permalink = data.get('permalink')
        
        user = self.context.get('request').user
        data['artist'] = user

        detail = {}
        track = self.instance

        if audio_filename is not None:
            audio_url = settings.S3_BASE_URL + settings.S3_MUSIC_TRACK_DIR + audio_filename
            if (track is None or getattr(track, 'audio') != audio_url) and Track.objects.filter(audio=audio_url).exists():
                detail['audio_filename'] = "Already existing audio file name."
            data['audio'] = audio_url

        if image_filename is not None:
            image_url = settings.S3_BASE_URL + settings.S3_IMAGES_TRACK_DIR + image_filename
            if (track is None or getattr(track, 'image') != image_url) and Track.objects.filter(image=image_url).exists():
                detail['image_filename'] = "Already existing image file name."
            data['image'] = image_url

        if permalink is not None:
            if (track is None or getattr(track, 'permalink') != permalink) and user.owned_tracks.filter(permalink=permalink).exists():
                detail['permalink'] = "Already existing permalink for the user."

        if any(detail):
            raise ConflictError(detail)

        return data


class TrackUploadSerializer(TrackSerializer):

    audio_presigned_url = serializers.SerializerMethodField()
    image_presigned_url = serializers.SerializerMethodField()

    class Meta(TrackSerializer.Meta):
        fields = TrackSerializer.Meta.fields + (
            'audio_presigned_url',
            'image_presigned_url',
        )

    def get_audio_presigned_url(self, track):
        audio_filename = track.audio.replace(settings.S3_BASE_URL, '')

        audio_presigned_url = boto3.client(
            's3',
            region_name=settings.S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ).generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': settings.S3_BUCKET_NAME,
                    'Key': settings.S3_MUSIC_TRACK_DIR + audio_filename},
            ExpiresIn=300
        )

        return audio_presigned_url

    def get_image_presigned_url(self, track):
        if track.image is not None:
            image_filename = track.image.replace(settings.S3_BASE_URL, '')

            image_presigned_url = boto3.client(
                's3',
                region_name=settings.S3_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            ).generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': settings.S3_BUCKET_NAME,
                        'Key': settings.S3_IMAGES_TRACK_DIR + image_filename},
                ExpiresIn=300
            )
        else:
            image_presigned_url = None

        return image_presigned_url


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
