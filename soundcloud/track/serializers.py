from django.conf import settings
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound, NotAuthenticated
from rest_framework.serializers import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from datetime import datetime
from soundcloud.exceptions import ConflictError
from track.models import Track
from comment.models import Comment
from user.serializers import UserSerializer
from tag.serializers import TagSerializer
from reaction.serializers import LikeSerializer, RepostSerializer
import boto3
import re


class CommentSerializer(serializers.ModelSerializer):
    writer = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'writer',
            'content',
            'created_at',
            'commented_at',
            'parent_comment'
        )


class PostCommentService(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=True, allow_null=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def execute(self):
        self.is_valid(raise_exception=True)

        user = self.context['request'].user
        if not user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        track_id = self.context['track_id']
        track = get_object_or_404(Track, id=track_id)
        content = self.validated_data.get('content')
        parent_comment_id = self.validated_data.get('parent_id')
        parent_comment = get_object_or_404(Comment, id=parent_comment_id) if parent_comment_id else None
        if parent_comment and Comment.objects.filter(writer=user, track=track, parent_comment=parent_comment):
            raise ConflictError("Comment already exists on this parent.")

        Comment.objects.create(writer=user,
                               track=track,
                               content=content,
                               commented_at=datetime.now(),
                               parent_comment=parent_comment)

        return status.HTTP_201_CREATED, "Comment created."


class DeleteCommentService(serializers.Serializer):

    def execute(self):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        current_comment = self.context['comment']
        parent_comment = current_comment.parent_comment
        child_comment = current_comment.reply
        current_comment.delete()
        if child_comment:
            child_comment.parent_comment = parent_comment
            child_comment.save()

        return status.HTTP_200_OK, "Comment deleted."


class RetrieveCommentService(serializers.Serializer):

    def execute(self):
        track_id = self.context['track_id']
        track = get_object_or_404(Track, id=track_id)
        comments = Comment.objects.filter(track=track)

        return status.HTTP_200_OK, comments


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

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, track):
        return track.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, track):
        return track.reposts.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_comment_count(self, track):
        return track.comment_set.count()


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
        detail = dict()

        audio_url = settings.S3_BASE_URL + settings.S3_MUSIC_TRACK_DIR + audio_filename
        if Track.objects.filter(audio=audio_url).exists():
            detail['audio_filename'] = "Already existing audio file name."

        if image_filename is not None:
            image_url = settings.S3_BASE_URL + settings.S3_IMAGES_TRACK_DIR + image_filename
            if Track.objects.filter(image=image_url).exists():
                detail['image_filename'] = "Already existing image file name."

        # Check if the same permalink already exists in database.
        if user.owned_tracks.filter(permalink=permalink).exists():
            detail['permalink'] = "Already existing permalink."

        if detail:
            raise ConflictError(detail)

        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        audio_filename = validated_data.pop('audio_filename')
        image_filename = validated_data.pop('image_filename', None)

        audio_url = settings.S3_BASE_URL + settings.S3_MUSIC_TRACK_DIR + audio_filename
        image_url = settings.S3_BASE_URL + settings.S3_IMAGES_TRACK_DIR + image_filename \
            if image_filename is not None \
            else None

        validated_data.update(
            {'artist': user, 'audio': audio_url, 'image': image_url}
        )

        track = super().create(validated_data)
        data = TrackUploadSerializer(track).data

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
