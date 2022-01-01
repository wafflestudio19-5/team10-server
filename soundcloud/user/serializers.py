from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework_jwt.settings import api_settings
#from soundcloud.exceptions import ConflictError
from datetime import date
from soundcloud.utils import ConflictError
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
    age = serializers.IntegerField(min_value=1, write_only=True)
    gender = serializers.CharField(write_only=True, required=False)

    def get_token(self, user):
        return jwt_token_of(user)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ConflictError({'email': "Already existing email."})

        return value

    def validate(self, data):
        age = data.pop('age')
        data['birthday'] = date(date.today().year-age, date.today().month, 1)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


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

    age = serializers.IntegerField(min_value=1, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'permalink',
            'display_name',
            'email',
            'password',
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

    def validate_password(self, value):
        
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if bool(first_name) != bool(last_name):
            raise serializers.ValidationError("Both of the first name and the last name must be entered.")

        age = data.pop('age', None)
        if age is not None:
            data['birthday'] = date(date.today().year-age, date.today().month, 1)

        return data


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'permalink',
            'email',
            'first_name',
            'last_name',
        )


class UserFollowService(serializers.Serializer):

    def create(self):
        follower = self.context['request'].user
        followee = self.context['user']

        if follower == followee:
            raise serializers.ValidationError("You cannot follow yourself.")

        if Follow.objects.filter(follower=follower, followee=followee).exists():
            raise serializers.ValidationError("Already followed")

        Follow.objects.create(follower=follower, followee=followee)
        return status.HTTP_201_CREATED, "Successful"

    def delete(self):
        follower = self.context['request'].user
        followee = self.context['user']

        follow = get_object_or_404(Follow, follower=follower, followee=followee)
        follow.delete()
        return status.HTTP_204_NO_CONTENT, "Successful"


class FollowerRetrieveService(serializers.Serializer):

    def execute(self):
        user = get_object_or_404(User, id=self.context['user_id'])
        return status.HTTP_200_OK, user.followed_by.values_list('follower', flat=True)


class FolloweeRetrieveService(serializers.Serializer):

    def execute(self):
        user = get_object_or_404(User, id=self.context['user_id'])
        return status.HTTP_200_OK, user.follows.values_list('followee', flat=True)
