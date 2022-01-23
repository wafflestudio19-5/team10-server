from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, status
from rest_framework_jwt.settings import api_settings
from soundcloud.utils import ConflictError, MediaUploadMixin, get_presigned_url
from datetime import date
from track.models import Track
from user.models import Follow

# 토큰 사용을 위한 기본 세팅
User = get_user_model()
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


# [ user -> jwt_token ] function
def jwt_token_of(user):
    payload = JWT_PAYLOAD_HANDLER(user)
    jwt_token = JWT_ENCODE_HANDLER(payload)

    return jwt_token


class UserCreateSerializer(serializers.Serializer):
    # Read-only fields
    id = serializers.IntegerField(read_only=True)
    permalink = serializers.SlugField(read_only=True)
    token = serializers.SerializerMethodField()

    # Write-only fields
    email = serializers.EmailField(max_length=100, write_only=True)
    display_name = serializers.CharField(max_length=25, write_only=True)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    age = serializers.IntegerField(min_value=1, write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)

    def get_token(self, user):
        return jwt_token_of(user)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ConflictError({'email': "Already existing email."})

        return value

    def validate(self, data):
        age = data.pop('age', None)
        if age is not None:
            data['birthday'] = date(date.today().year-age, date.today().month, 1)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class UserSocialLoginSerializer(serializers.Serializer):
    # Read-only fields
    id = serializers.IntegerField(read_only=True)
    permalink = serializers.SlugField(read_only=True)
    token = serializers.SerializerMethodField()

    # Write-only fields
    email = serializers.EmailField(write_only=True)

    def get_token(self, user):
        return jwt_token_of(user)

    def validate(self, data):
        email = data.pop('email')
        try:
            user = User.objects.get(email=email)
            self.instance = user
        except User.DoesNotExist:
            raise serializers.ValidationError("이메일이 잘못되었습니다.")

        return data

    def execute(self):
        update_last_login(None, self.instance)


class UserLoginSerializer(serializers.Serializer):

    # Read-only fields
    id = serializers.IntegerField(read_only=True)
    permalink = serializers.SlugField(read_only=True)
    token = serializers.SerializerMethodField()

    # Write-only fields
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def get_token(self, user):
        return jwt_token_of(user)

    def validate(self, data):
        email = data.pop('email')
        password = data.pop('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")
        else:
            self.instance = user

        return data

    def execute(self):
        update_last_login(None, self.instance)


class UserSerializer(serializers.ModelSerializer):

    image_profile = serializers.SerializerMethodField()
    image_header = serializers.SerializerMethodField()
    age = serializers.IntegerField(min_value=1, write_only=True, required=False)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    track_count = serializers.SerializerMethodField()
    like_track_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'permalink',
            'display_name',
            'email',
            'password',
            'image_profile',
            'image_header',
            'follower_count',
            'following_count',
            'track_count',
            'like_track_count',
            'comment_count',
            'created_at',
            'last_login',
            'age',
            'birthday',
            'is_active',
            'gender',
            'first_name',
            'last_name',
            'city',
            'country',
            'bio',
            'path', #add
            'is_followed',
        )
        extra_kwargs = {
            'permalink': {
                'max_length': 25,
                'min_length': 3,
            },
            'password': {
                'write_only': True,
                'max_length': 128,
                'min_length': 8,
            },
        }
        read_only_fields = (
            'created_at',
            'last_login',
            'birthday',
            'is_active',
        )

    def get_image_profile(self, user):
        return get_presigned_url(user.image_profile, 'get_object')

    def get_image_header(self, user):
        return get_presigned_url(user.image_header, 'get_object')

    @extend_schema_field(OpenApiTypes.INT)
    def get_follower_count(self, user):
        return user.followers.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_following_count(self, user):
        return user.followings.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_track_count(self, user):
        return user.owned_tracks.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_track_count(self, user):
        content_type = ContentType.objects.get_for_model(Track)

        return user.likes.filter(content_type=content_type).count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_comment_count(self, user):
        return user.comments.count()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_followed(self, user):
        return bool(Follow.objects.filter(follower=self.context['request'].user, followee=user))

    def validate_password(self, value):

        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if bool(first_name) != bool(last_name):
            raise serializers.ValidationError("Both of the first name and the last name must be entered.")

        age = data.pop('age', None)
        if age is not None:
            data['birthday'] = date(date.today().year - age, date.today().month, 1)

        return data


class UserMediaUploadSerializer(MediaUploadMixin, UserSerializer):

    image_profile_extension = serializers.CharField(write_only=True, required=False)
    image_header_extension = serializers.CharField(write_only=True, required=False)
    image_profile_presigned_url = serializers.SerializerMethodField()
    image_header_presigned_url = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'image_profile_extension',
            'image_header_extension',
            'image_profile_presigned_url',
            'image_header_presigned_url',
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.extensions_to_urls(data)

        return data


class SimpleUserSerializer(serializers.ModelSerializer):

    image_profile = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    track_count = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'permalink',
            'display_name',
            'email',
            'image_profile',
            'follower_count',
            'track_count',
            'first_name',
            'last_name',
            'is_followed',
        )

    def get_image_profile(self, user):
        return get_presigned_url(user.image_profile, 'get_object')

    @extend_schema_field(OpenApiTypes.INT)
    def get_follower_count(self, user):
        return user.followers.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_track_count(self, user):
        return user.owned_tracks.count()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_followed(self, user):
        return bool(Follow.objects.filter(follower=self.context['request'].user, followee=user))

      
class UserFollowService(serializers.Serializer):

    def create(self):
        follower = self.context['request'].user
        followee = self.context['user']

        if follower == followee:
            raise serializers.ValidationError("You cannot follow yourself.")

        if Follow.objects.filter(follower=follower, followee=followee).exists():
            raise serializers.ValidationError("Already followed.")

        Follow.objects.create(follower=follower, followee=followee)
        return status.HTTP_201_CREATED, "Successful"

    def delete(self):
        follower = self.context['request'].user
        followee = self.context['user']

        try:
            follow = Follow.objects.get(follower=follower, followee=followee)
        except Follow.DoesNotExist:
            raise serializers.ValidationError("Haven't followed yet.")

        follow.delete()
        return status.HTTP_204_NO_CONTENT, "Successful"

