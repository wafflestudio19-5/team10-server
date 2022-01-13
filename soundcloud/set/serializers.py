from re import T
from set.models import Set, SetTrack
from track.models import Track
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator
from user.serializers import SimpleUserSerializer
from tag.serializers import TagSerializer
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from soundcloud.utils import get_presigned_url, MediaUploadMixin
from rest_framework.serializers import ValidationError
from track.serializers import SetTrackSerializer, TrackMediaUploadSerializer

class SetSerializer(serializers.ModelSerializer):
    creator = SimpleUserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    image_profile = serializers.SerializerMethodField()
    image_header = serializers.SerializerMethodField()
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tracks = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Set
        fields = (
            'id',
            'title',
            'creator',
            'permalink',
            'type',
            'description',
            'genre',
            'tags',
            'is_private',
            'like_count',
            'repost_count',
            'image_profile',
            'image_header',
            'tracks', #tracks in set
            'created_at',
        )        
        extra_kwargs = {
            'permalink': {
                'max_length': 255,
                'min_length': 3,
            },
            'created_at': {'read_only': True},
        
        }

        # Since 'creator' is read-only field, ModelSerializer wouldn't generate UniqueTogetherValidator automatically.
        validators = [
            UniqueTogetherValidator(
                queryset=Set.objects.all(),
                fields=('creator', 'permalink'),
                message="Already existing set permalink for the requested user."
            ),
        ]

    def get_image_profile(self, set):
        return get_presigned_url(set.image_profile, 'get_object')

    def get_image_header(self, set):
        return get_presigned_url(set.image_header, 'get_object')


    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, set):
        return set.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, set):
        return set.reposts.count()

    def get_tracks(self, set):
        set_tracks = set.set_tracks.all()
        tracks = []
        for set_track in set_tracks:
            tracks.append(set_track.track)
        if not set_tracks.count():
            return None
        return SetTrackSerializer(tracks, many=True, context=self.context).data

    def validate_permalink(self, value):
        if not any(c.isalpha() for c in value):
            raise ValidationError("Permalink must contain at least one alphabetic character.")
        return value

    def validate(self, data):

        # Although it has default value, should manually include 'creator' to the data because it is read-only field.
        if self.instance is None:
            data['creator'] = self.context['request'].user

        return data



class SetMediaUploadSerializer(MediaUploadMixin, SetSerializer): #이거는 put에서만 쓰기. 이미지 수정용 
    
    image_profile_filename = serializers.CharField(write_only=True, required=False)
    image_header_filename = serializers.CharField(write_only=True, required=False)
    image_profile_presigned_url = serializers.SerializerMethodField()
    image_header_presigned_url = serializers.SerializerMethodField()


    class Meta(SetSerializer.Meta):
        fields = SetSerializer.Meta.fields + (
            'image_profile_filename',
            'image_profile_presigned_url',
            'image_header_filename',
            'image_header_presigned_url',
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.filenames_to_urls(data)

        return data


