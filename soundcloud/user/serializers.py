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
    display_name = serializers.CharField(max_length=25)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=128, write_only=True)
    age = serializers.IntegerField()
    gender = serializers.CharField(max_length=20, required=False)

    def validate(self, data):
        age = data.pop('age')
        password = data.get('password')
        if age < 0:
            raise serializers.ValidationError("나이에는 양의 정수만 입력가능합니다.")
        if len(password) < 8:
            raise serializers.ValidationError("비밀번호는 8자리 이상 입력해야합니다.")

        data.update(
            {'birthday': date(date.today().year-age,
                              date.today().month, 1)}
        )

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return {
            'permalink': user.permalink,
            'token': jwt_token_of(user)
        }


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.pop('email')
        password = data.pop('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")

        update_last_login(None, user)
        
        return {
            'permalink': user.permalink,
            'token': jwt_token_of(user)
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'permalink',
            'display_name',
            'email',
            'created_at',
            'last_login',
            'birthday',
            'gender',
            'password',
            'first_name',
            'last_name',
            'city',
            'country',
            'bio',
        )
        extra_kwargs = {'created_at': {'read_only': True}, 'last_login': {
            'read_only': True}, 'password': {'write_only': True}}
