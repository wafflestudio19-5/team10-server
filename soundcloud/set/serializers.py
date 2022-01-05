from re import T
from set.models import Set, SetTrack
from reaction.models import Like, Repost
from track.models import Track
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator
from user.serializers import UserSerializer
from tag.serializers import TagSerializer
from reaction.serializers import RepostSerializer
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from soundcloud.utils import get_presigned_url
from rest_framework.serializers import ValidationError
from django.contrib.contenttypes.models import ContentType


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
            'is_like',
            'repost',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    def get_is_like(self, track):
        if self.context['request'].user.is_authenticated:
            try:                	
                contenttype_obj = ContentType.objects.get_for_model(track)
                Like.objects.get(user=self.context['request'].user, object_id=track.id, content_type=contenttype_obj)
                return True
            except Like.DoesNotExist:
                return False
        else: 
            return False 

    def get_repost(self, track):
        if self.context['request'].user.is_authenticated:
            try:                	
                contenttype_obj = ContentType.objects.get_for_model(track)
                repost = Repost.objects.get(user=self.context['request'].user, object_id=track.id, content_type=contenttype_obj)
                return RepostSerializer(repost, context=self.context).data
            except Repost.DoesNotExist:
                return None
        else: 
            return None 






class SetUploadSerializer(SetSerializer):
    image_presigned_url = serializers.SerializerMethodField()
    class Meta(SetSerializer.Meta):
        fields = SetSerializer.Meta.fields + (
            'image_presigned_url',
        )
    
    #트랙 시리얼라이저에서 가져옴
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

    

    #track/settrack 생성까지.