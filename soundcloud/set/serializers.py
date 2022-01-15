from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from set.models import Set
from set.models import SetTrack
from track.models import Track
from soundcloud.utils import get_presigned_url, MediaUploadMixin
from tag.serializers import TagSerializer
from track.serializers import TrackInSetSerializer
from user.serializers import SimpleUserSerializer


class SetSerializer(serializers.ModelSerializer):
    creator = SimpleUserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
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

    def get_image(self, set):
        return get_presigned_url(set.image, 'get_object')


    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, set):
        return set.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, set):
        return set.reposts.count()

    def get_tracks(self, set):
        tracks = set.tracks.all()
        if not tracks:
            return None
        return TrackInSetSerializer(tracks, many=True, context=self.context).data

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
    image_extension = serializers.CharField(write_only=True, required=False)
    image_presigned_url = serializers.SerializerMethodField()


    class Meta(SetSerializer.Meta):
        fields = SetSerializer.Meta.fields + (
            'image_extension',
            'image_presigned_url',
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.extensions_to_urls(data)

        return data

# class SetTrackService(serializers.ModelSerializer):
#     track = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(), required=True)
#     set = SetSerializer(read_only=True)

# class TrackPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
#     def display_value(self, instance):
#         return 'Track: %s' % (instance.title)

class SetTrackService(serializers.Serializer):

    def create(self):
        set = self.context['set']
        track = self.context['track']
        if track is None:
            return status.HTTP_400_BAD_REQUEST, {"error": "track_id 는 필수입니다."}
        if set.tracks.filter(id=track.id).exists():
            return status.HTTP_400_BAD_REQUEST, {"error": "이미 셋에 추가되어 있습니다."}

        set.tracks.add(track)
        set.save()
        return status.HTTP_200_OK, {"added to playlist."}
    
    def delete(self):
        set = self.context['set']
        track = self.context['track']
        if track is None:
            return status.HTTP_400_BAD_REQUEST, {"error": "track_id 는 필수입니다."}
        if set.tracks.filter(id=track.id).exists():
            set.tracks.remove(track)
            return status.HTTP_204_NO_CONTENT, None
    
        return status.HTTP_400_BAD_REQUEST, {"error": "셋에 없는 트랙입니다."}





