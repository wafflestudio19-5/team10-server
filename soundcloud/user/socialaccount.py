from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from user.views import *
from soundcloud.settings.common import *
from django.db import transaction
import copy
from django.contrib.auth import login
from drf_spectacular.utils import OpenApiResponse, extend_schema
from django.contrib.auth.backends import ModelBackend


User = get_user_model()

class SocialAccountApi(APIView):
    permission_classes = (permissions.AllowAny, )
    def social_user_login(self, user, data): #jwt_login()
        login(self.request, user, 'user.socialaccount.GoogleBackend')  # GoogleBackend 를 통한 인증 시도
        serializer = UserSocialLoginSerializer(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.execute()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
        
    @transaction.atomic
    def social_user_create(self, email, **extra_fields):
        data = copy.deepcopy(extra_fields)
        data["email"]=email
        data["password"]=settings.SOCIAL_PASSWORD

        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return self.social_user_login(user, data) #회원가입 후 소셜로그인

    @transaction.atomic
    def social_user_get_or_create(self, email, **extra_data):
        data = copy.deepcopy(extra_data)
        data["email"]=email

        try: #이미 존재하는 이메일이면 소셜로그인.
            user = User.objects.get(email=email)
            return self.social_user_login(user, data)
            
        except User.DoesNotExist: #회원가입부터
            return self.social_user_create(email=email, **extra_data)            


    @extend_schema(
        summary="Social User Signup/Login",
        tags=['auth', ],
        responses={
            200: OpenApiResponse(response=UserSocialLoginSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def put(self, request, *args, **kwargs): 
        user_data = request.data.copy()
        profile_data = { 
            'email': user_data['email'],  #username->email
            'first_name': user_data.get('given_name', ''), 
            'last_name': user_data.get('family_name', ''), 
            'display_name': user_data.get('name', 'NoName'), 
            'path': "google", 
            }  #구글이 넘겨주는 거.


        return self.social_user_get_or_create(**profile_data) 


class GoogleBackend(ModelBackend):
    def authenticate(self, request, email=None, **kwargs):
        if email is None:
            email = kwargs.get(User.EMAIL_FIELD)
        try:
            user = User._default_manager.get_by_natural_key(email)
        except User.DoesNotExist:
            pass
        else:
            if self.user_can_authenticate(user):
                return user


