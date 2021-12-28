from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from datetime import date
import re

# 토큰 사용을 위한 기본 세팅
User = get_user_model()
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


# [ user -> jwt_token ] function
def jwt_token_of(user):
    payload = JWT_PAYLOAD_HANDLER(user)
    jwt_token = JWT_ENCODE_HANDLER(payload)

    return jwt_token

def create_permalink():
    while True:
        permalink = User.objects.make_random_password(
            length=12, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
        if not User.objects.filter(permalink=permalink).exists():
            return permalink


class UserCreateSerializer(serializers.Serializer):

    # Read-only fields
    id = serializers.IntegerField(read_only=True)
    permalink = serializers.CharField(read_only=True)
    token = serializers.SerializerMethodField()

    # Write-only fields
    email = serializers.EmailField(max_length=100, write_only=True)
    display_name = serializers.CharField(max_length=25, write_only=True)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    age = serializers.IntegerField(min_value=1, write_only=True)
    gender = serializers.CharField(write_only=True, required=False)

    def get_token(self, user):
        return jwt_token_of(user)

    def validate(self, data):
        age = data.pop('age')
        data['birthday'] = date(date.today().year-age, date.today().month, 1)

        return data

    def create(self, validated_data):
        validated_data['permalink'] = create_permalink()
        user = User.objects.create_user(**validated_data)

        return UserCreateSerializer(user).data


class UserLoginSerializer(serializers.Serializer):

    # Read_only fields
    id = serializers.IntegerField(read_only=True)
    permalink = serializers.CharField(read_only=True)
    token = serializers.SerializerMethodField()

    # Write-only fields
    email = serializers.EmailField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    def get_token(self, user):
        return jwt_token_of(user)

    def validate(self, data):
        email = data.pop('email')
        password = data.pop('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")

        self.context['user'] = user
        return data

    def execute(self):
        user = self.context.get('user')
        update_last_login(None, user)

        return UserLoginSerializer(user).data


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

    def validate_permalink(self, value):
        pattern = re.compile('^[a-z0-9\-\_]+$')

        if not re.search(pattern, value):
            raise serializers.ValidationError("Only lowercase letters/numbers/_/- are allowed in permalink.")

        return value

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
