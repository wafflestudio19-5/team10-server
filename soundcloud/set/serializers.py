from set.models import Set, SetTrack
from track.models import Track
from rest_framework import serializers
from rest_framework.response import Response
from user.serializers import UserSerializer
from tag.serializers import TagSerializer
from reaction.serializers import LikeSerializer, RepostSerializer
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

class SetSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tracks = serializers.SerializerMethodField()

    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()

    likes = LikeSerializer(many=True, read_only=True)
    reposts = RepostSerializer(many=True, read_only=True)

    image_filename = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Set
        fields = (
            'id',
            'title',
            'creator',
            'type',
            'description',
            'tags',
            'is_private',
            'likes',
            'reposts',
            'like_count',
            'repost_count',
            'image',
            'image_filename',
            'tracks',
        )        
        extra_kwargs = {
            'image' : {'read_only': True},
            'created_at': {'read_only': True},
            'count': {'read_only': True},
        }

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, set):
        return set.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, set):
        return set.reposts.count()

    def get_tracks(self, set):
        tracks = set.set_tracks.all()
        return SetTrackSerializer(tracks, many=True, context=self.context).data


class SetTrackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Track
        fields = (
            'id'
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'count',
        )
        extra_kwargs = {
            'audio': {'read_only': True},
            'image': {'read_only': True},
            'count': {'read_only': True},
        }




class SetUploadSerializer(SetSerializer):
#track/settrack 생성까지.