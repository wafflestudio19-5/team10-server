from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ValidationError
from soundcloud.utils import get_presigned_url, MediaUploadMixin
from tag.models import Tag
from tag.serializers import TagSerializer
from track.models import Track
from user.models import Follow
from user.serializers import UserSerializer, SimpleUserSerializer
from reaction.serializers import LikeService, RepostService
from reaction.models import Like, Repost
from soundcloud.utils import assign_object_perms, get_presigned_url, MediaUploadMixin
from django.contrib.contenttypes.models import ContentType


class TrackSerializer(serializers.ModelSerializer):

    artist = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    genre_input = serializers.CharField(max_length=20, required=False)
    tags_input = serializers.ListField(child=serializers.CharField(max_length=20), required=False)
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_reposted = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'like_count',
            'repost_count',
            'comment_count',
            'description',
            'created_at',
            'count',
            'genre',
            'tags',
            'genre_input',
            'tags_input',
            'is_private',
            'is_liked',
            'is_reposted',
            'is_followed',
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
            'genre_input',
            'tags_input',
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
        return track.comments.count()
    
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

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_followed(self, track):
        if self.context['request'].user.is_authenticated:
            follower = self.context['request'].user
            followee = track.artist
            try:
                Follow.objects.get(follower=follower, followee=followee)
                return True
            except Follow.DoesNotExist:
                return False
        else:
            return False

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
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'like_count',
            'repost_count',
            'comment_count',
            'genre',
            'count',
            'is_private',
            'is_liked',
            'is_followed',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    def get_like_count(self, track):
        return track.likes.count()

    def get_repost_count(self, track):
        return track.reposts.count()

    def get_comment_count(self, track):
        return track.comments.count()
    
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
    def get_is_followed(self, track):
        if self.context['request'].user.is_authenticated:
            follower = self.context['request'].user
            followee = track.artist
            try:
                Follow.objects.get(follower=follower, followee=followee)
                return True
            except Follow.DoesNotExist:
                return False
        else:
            return False


class UserTrackSerializer(serializers.ModelSerializer):

    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'permalink',
            'audio',
            'image',
            'like_count',
            'repost_count',
            'comment_count',
            'genre',
            'count',
            'is_private',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    def get_like_count(self, track):
        return track.likes.count()

    def get_repost_count(self, track):
        return track.reposts.count()

    def get_comment_count(self, track):
        return track.comments.count()

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
    artist_permalink = serializers.CharField(source='artist.permalink')
    artist_display_name = serializers.CharField(source='artist.display_name')
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_reposted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'artist_permalink',
            'artist_display_name',
            'permalink',
            'audio',
            'image',
            'count',
            'is_liked',
            'is_reposted',
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
