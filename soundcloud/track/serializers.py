from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ValidationError
from track.models import Track
from tag.serializers import TagSerializer
from user.serializers import UserSerializer
from reaction.serializers import LikeSerializer, RepostSerializer
from soundcloud.utils import get_presigned_url, MediaUploadMixin


class TrackSerializer(serializers.ModelSerializer):

    artist = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    likes = LikeSerializer(many=True, read_only=True)
    reposts = RepostSerializer(many=True, read_only=True)
    # comments = CommentSerializer(many=True, read_only=True)

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
            # 'comments',
        )
        extra_kwargs = {
            'permalink': {
                'max_length': 255,
                'min_length': 3,
            },
        }
        read_only_fields = (
            'created_at',
            'count',
        )

        # Since 'artist' is read-only field, ModelSerializer wouldn't generate UniqueTogetherValidator automatically.
        validators = [
            UniqueTogetherValidator(
                queryset=Track.objects.all(),
                fields=('artist', 'permalink'),
                message="Already existing permalink for the requested user."
            ),
        ]

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, track):
        return track.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, track):
        return track.reposts.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_comment_count(self, track):
        return track.comment_set.count()

    def validate_permalink(self, value):
        if not any(c.isalpha() for c in value):
            raise ValidationError("Permalink must contain at least one alphabetic character.")

        return value

    def validate(self, data):

        # Although it has default value, should manually include 'artist' to the data because it is read-only field.
        if self.instance is None:
            data['artist'] = self.context['request'].user

        return data
    

class TrackMediaUploadSerializer(TrackSerializer, MediaUploadMixin):

    audio_filename = serializers.CharField(write_only=True)
    image_filename = serializers.CharField(write_only=True, required=False)
    audio_presigned_url = serializers.SerializerMethodField()
    image_presigned_url = serializers.SerializerMethodField()

    class Meta(TrackSerializer.Meta):
        fields = TrackSerializer.Meta.fields + (
            'audio_filename',
            'image_filename',
            'audio_presigned_url',
            'image_presigned_url',
        )

    def get_audio_presigned_url(self, track):
        if self.context['request'].data.get('audio_filename') is None:
            return None

        return get_presigned_url(track.audio, 'put_object')

    def get_image_presigned_url(self, track):
        if self.context['request'].data.get('image_filename') is None:
            return None

        return get_presigned_url(track.image, 'put_object')
    
    def validate_audio_filename(self, value):
        if not self.check_extension(value, 'audio'):
            raise ValidationError("Unsupported audio file extension.")

        if not self.check_filename(value):
            raise ValidationError("Incorrect audio filename format.")

        return value

    def validate_image_filename(self, value):
        if not self.check_extension(value, 'image'):
            raise ValidationError("Unsupported image file extension.")

        if not self.check_filename(value):
            raise ValidationError("Incorrect image filename format.")

        return value

    def validate(self, data):
        data = super().validate(data)
        audio_filename = data.pop('audio_filename', None)
        image_filename = data.pop('image_filename', None)

        # Generate unique audio url or image url, and include them to the data.
        if audio_filename is not None:
            data['audio'] = self.get_unique_url(audio_filename, 'audio', 'track')
        if image_filename is not None:
            data['image'] = self.get_unique_url(image_filename, 'image', 'track')

        return data


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
