from re import T
from set.models import Set, SetTrack
from track.models import Track
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator
from user.serializers import UserSerializer
from tag.serializers import TagSerializer
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from soundcloud.utils import get_presigned_url, MediaUploadMixin
from rest_framework.serializers import ValidationError
from track.serializers import SetTrackSerializer, TrackMediaUploadSerializer

class SetSerializer(serializers.ModelSerializer):
    creator = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    image = serializers.SerializerMethodField()
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
            'image',
            'tracks', #tracks in set
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

    def get_image(self, set):
        return get_presigned_url(set.image, 'get_object')

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, set):
        return set.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, set):
        return set.reposts.count()

    def get_tracks(self, set):
        tracks = set.set_tracks.all()
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


class SetUploadSerializer(MediaUploadMixin, SetSerializer):
    image_filename = serializers.CharField(write_only=True, required=False)
    image_presigned_url = serializers.SerializerMethodField()
    upload_tracks = serializers.SerializerMethodField()

    class Meta(SetSerializer.Meta):
        fields = SetSerializer.Meta.fields + (
            'image_filename',
            'image_presigned_url',
            'upload_tracks',
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.filenames_to_urls(data)

        return data

    def get_upload_tracks(self, data, set):
        tracks_data = data['tracks']
        for track_data in tracks_data:
            data_track = {}
            data_track['title']=track_data['title']
            data_track['permalink']=track_data['permalink']
            data_track['description']=data['description'] #set과 동일
            data_track['is_private']=data['is_private'] #set과 동일
            data_track['image_filename']=data['image_filename'] #set과 동일
            data_track['audio_filename']=track_data['audio_filename']
            # 장르, 태그는 set 따라. 일단 track request body에 없어서 뺌.

            track = TrackMediaUploadSerializer(data_track).save()
            SetTrack.objects.create(set=set, track=track)

        
        queryset = Track.objects.none()
        setTracks = SetTrack.objects.filter(set=set)
        for setTrack in setTracks:
            queryset |= setTrack.track

        return SetTrackSerializer(queryset, many=True).data
