from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from set.models import Set
from user.models import Follow
from soundcloud.utils import get_presigned_url, MediaUploadMixin
from tag.models import Tag
from tag.serializers import TagSerializer
from track.serializers import TrackInSetSerializer
from user.serializers import SimpleUserSerializer
from reaction.models import Like, Repost


class SetSerializer(serializers.ModelSerializer):
    creator = SimpleUserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    image = serializers.SerializerMethodField()
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    genre_input = serializers.CharField(max_length=20, required=False, write_only=True)
    tags_input = serializers.ListField(child=serializers.CharField(max_length=20), required=False, write_only=True)
    tracks = serializers.SerializerMethodField()
    track_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    repost_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_reposted = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    
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
            'genre_input',
            'tags_input',
            'is_private',
            'track_count',
            'like_count',
            'repost_count',
            'image',
            'tracks', #tracks in set
            'created_at',
            'is_liked',
            'is_reposted',
            'is_followed', #for creator
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

    def get_tracks(self, set):
        tracks = set.tracks.order_by('set_tracks__created_at')
        if not tracks:
            return None
        return TrackInSetSerializer(tracks, many=True, context=self.context).data

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_liked(self, set):
        if self.context['request'].user.is_authenticated:
            try:                	
                Like.objects.get(user=self.context['request'].user, set=set)
                return True
            except Like.DoesNotExist:
                return False
        else: 
            return False 

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_reposted(self, set):
        if self.context['request'].user.is_authenticated:
            try:                	
                Repost.objects.get(user=self.context['request'].user, set=set)
                return True
            except Repost.DoesNotExist:
                return False
        else: 
            return False

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_followed(self, set):
        if self.context['request'].user.is_authenticated:
            follower = self.context['request'].user
            followee = set.creator
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

        # Although it has default value, should manually include 'creator' to the data because it is read-only field.
        if self.instance is None:
            data['creator'] = self.context['request'].user

        if 'genre_input' in data:
            genre_input = data.pop('genre_input')
            data['genre'] = Tag.objects.get_or_create(name=genre_input)[0]

        if 'tags_input' in data:
            genre = data.get('genre') or self.instance.genre
            genre_name = genre.name if genre else ""
            tags_input = data.pop('tags_input')
            data['tags'] = [Tag.objects.get_or_create(name=tag)[0] for tag in tags_input if tag != genre_name]


        return data


class SimpleSetSerializer(serializers.ModelSerializer):
    '''returns only first 5 tracks in the set'''
    creator = SimpleUserSerializer()
    image = serializers.SerializerMethodField()
    genre = TagSerializer()
    tracks = serializers.SerializerMethodField()
    track_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    repost_count = serializers.IntegerField()
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_reposted = serializers.SerializerMethodField(read_only=True)
    
    
    
    class Meta:
        model = Set
        fields = (
            'id',
            'title',
            'creator',
            'permalink',
            'type',
            'genre',
            'is_private',
            'track_count',
            'like_count',
            'repost_count',
            'image',
            'tracks',
            'is_liked',
            'is_reposted',
        )

    def get_image(self, set):
        return get_presigned_url(set.image, 'get_object')

    @extend_schema_field(TrackInSetSerializer(many=True))
    def get_tracks(self, set):
        tracks = set.tracks.all().order_by('set_tracks__created_at')[:5]

        return TrackInSetSerializer(tracks, many=True, context=self.context).data
    
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_liked(self, set):
        if self.context['request'].user.is_authenticated:
            try:                	
                Like.objects.get(user=self.context['request'].user, set=set)
                return True
            except Like.DoesNotExist:
                return False
        else: 
            return False 

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_reposted(self, set):
        if self.context['request'].user.is_authenticated:
            try:                	
                Repost.objects.get(user=self.context['request'].user, set=set)
                return True
            except Repost.DoesNotExist:
                return False
        else: 
            return False


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


class SetTrackService(serializers.Serializer):
    track_id = serializers.IntegerField(write_only=True)
    
    def create(self):
        set = self.context['set']
        track_ids = self.context['track_ids']

        if track_ids is None or track_ids == []:
            return status.HTTP_400_BAD_REQUEST, {"error": "track_ids 는 필수입니다."}

        tracks_num = len(track_ids)
        tracks_id = []
        for d in track_ids:
            tracks_id.append(d["id"])
        tracks = Track.objects.filter(id__in=tracks_id)

        if tracks.count() != tracks_num:
            return status.HTTP_400_BAD_REQUEST, {"error": "track_ids 가 유효하지 않습니다."}

        if set.tracks.filter(id__in=tracks_id).exists():
            return status.HTTP_400_BAD_REQUEST, {"error": "이미 셋에 추가된 트랙이 있습니다."}

        set.tracks.add(*tracks)
        set.save()

        return status.HTTP_200_OK, {"all added to playlist."}
    
    def delete(self):
        set = self.context['set']
        track_ids = self.context['track_ids']

        if track_ids is None or track_ids == []:
            return status.HTTP_400_BAD_REQUEST, {"error": "track_ids 는 필수입니다."}

        tracks_num = len(track_ids)
        tracks_id = []
        for d in track_ids:
            tracks_id.append(d["id"])
        tracks = Track.objects.filter(id__in=tracks_id)

        if tracks.count() != tracks_num:
            return status.HTTP_400_BAD_REQUEST, {"error": "track_ids 가 유효하지 않습니다."}

        if set.tracks.filter(id__in=tracks_id).count() != tracks_num:
            return status.HTTP_400_BAD_REQUEST, {"error": "셋에 없는 트랙이 포함되어 있습니다."}

        set.tracks.remove(*tracks)
        set.save()
        
        return status.HTTP_204_NO_CONTENT, None
    
        





