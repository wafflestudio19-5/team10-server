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
    password = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(max_length=100)
    age = serializers.IntegerField()
    gender = serializers.CharField(max_length=20, required=False)


    def validate(self, data):
        age = data.get('age', 0)
        password = data.get('password', '')
        if age < 0:
            raise serializers.ValidationError("나이에는 양의 정수만 입력가능합니다.")
        if len(password) < 8:
            raise serializers.ValidationError("비밀번호는 8자리 이상 입력해야합니다.")
        return data

    def create(self, validated_data):
        display_name = validated_data.pop('display_name')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        age = validated_data.pop('age')
        gender = validated_data.pop('gender', '')
        birthday = date(date.today().year - age + 1, 1, 1)
        user = User.objects.create_user(display_name=display_name, email=email, birthday=birthday, gender=gender,
                                        password=password)
        user.profile_id = user.id
        user.save()
        return user, jwt_token_of(user)


class UserLoginSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(max_length=100)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")

        update_last_login(None, user)
        return {
            'display_name': user.display_name,
            'email': user.email,
            'token': jwt_token_of(user)
        }
