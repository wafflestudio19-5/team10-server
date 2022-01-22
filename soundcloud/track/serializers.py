from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ValidationError
from soundcloud.utils import get_presigned_url, MediaUploadMixin
from tag.models import Tag
from tag.serializers import TagSerializer
from track.models import Track, TrackHit
from user.serializers import UserSerializer, SimpleUserSerializer
from reaction.models import Like, Repost
from soundcloud.utils import get_presigned_url, MediaUploadMixin


class TrackSerializer(serializers.ModelSerializer):

    artist = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    genre_input = serializers.CharField(max_length=20, required=False, write_only=True)
    tags_input = serializers.ListField(child=serializers.CharField(max_length=20), required=False, write_only=True)
    play_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    repost_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'play_count',
            'like_count',
            'repost_count',
            'comment_count',
            'description',
            'created_at',
            'genre',
            'tags',
            'genre_input',
            'tags_input',
            'is_private',
        )
        extra_kwargs = {
            'permalink': {
                'max_length': 255,
                'min_length': 3,
            },
        }
        read_only_fields = (
            'created_at',
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

    def validate_permalink(self, value):
        if not any(c.isalpha() for c in value):
            raise ValidationError("Permalink must contain at least one alphabetic character.")

        return value

    def validate(self, data):

        # Although it has default value, should manually include 'artist' to the data because it is read-only field.
        if self.instance is None:
            data['artist'] = self.context['request'].user

        if 'genre_input' in data:
            genre_input = data.pop('genre_input')
            data['genre'] = Tag.objects.get_or_create(name=genre_input)[0]

        if 'tags_input' in data:
            genre = data.get('genre') or self.instance.genre
            genre_name = genre.name if genre else ""
            tags_input = data.pop('tags_input')
            data['tags'] = [Tag.objects.get_or_create(name=tag)[0] for tag in tags_input if tag != genre_name]

        return data


class TrackMediaUploadSerializer(MediaUploadMixin, TrackSerializer):

    audio_extension = serializers.CharField(write_only=True)
    image_extension = serializers.CharField(write_only=True, required=False)
    audio_presigned_url = serializers.SerializerMethodField()
    image_presigned_url = serializers.SerializerMethodField()

    class Meta(TrackSerializer.Meta):
        fields = TrackSerializer.Meta.fields + (
            'audio_extension',
            'image_extension',
            'audio_presigned_url',
            'image_presigned_url',
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.extensions_to_urls(data)

        return data


class SimpleTrackSerializer(serializers.ModelSerializer):
    
    artist = SimpleUserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    play_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    repost_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'play_count',
            'like_count',
            'repost_count',
            'comment_count',
            'genre',
            'is_private',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')


class UserTrackSerializer(serializers.ModelSerializer):

    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    play_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    repost_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'permalink',
            'audio',
            'image',
            'play_count',
            'like_count',
            'repost_count',
            'comment_count',
            'genre',
            'is_private',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')


class CommentTrackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'permalink',
            'is_private'
        )


class TrackInSetSerializer(serializers.ModelSerializer):
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_reposted = serializers.SerializerMethodField(read_only=True)
    play_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'is_liked',
            'is_reposted',
            'play_count',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_liked(self, track):
        if self.context['request'].user.is_authenticated:
            try:                	
                Like.objects.get(user=self.context['request'].user, track=track)
                return True
            except Like.DoesNotExist:
                return False
        else: 
            return False 

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_reposted(self, track):
        if self.context['request'].user.is_authenticated:
            try:                	
                Repost.objects.get(user=self.context['request'].user, track=track)
                return True
            except Repost.DoesNotExist:
                return False
        else: 
            return False 


class TrackHitService(serializers.Serializer):

    def execute(self):
        user = self.context.get('request').user
        user = user if user.is_authenticated else None
        obj, created = TrackHit.objects.get_or_create(user=user, track=self.instance)

        # update track's hit count and last play datetime
        obj.count = F('count') + 1
        obj.save()

        return status.HTTP_201_CREATED if created else status.HTTP_200_OK, "track hit success"
