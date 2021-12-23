from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from datetime import date

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

    def create(self, validated_data):
        age = validated_data.pop('age')
        validated_data['birthday'] = date(date.today().year-age, date.today().month, 1)
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
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'last_login': {'read_only': True},
            'birthday': {'read_only': True},
            'is_active': {'read_only': True}
        }
