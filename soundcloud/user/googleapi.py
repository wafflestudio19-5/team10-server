from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from user.services import google_get_access_token, google_get_user_info
from user.views import *
from soundcloud.settings.common import *
from django.db import transaction
import copy
from django.contrib.auth import login
from drf_spectacular.utils import OpenApiResponse, extend_schema
from django.contrib.auth.backends import ModelBackend


User = get_user_model()

class GoogleLoginApi(APIView):
    @extend_schema(
        summary="Google Login",
        tags=['auth', ],
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def get(self, request, *args, **kwargs): 
        client_id = get_secret("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        scope = "https://www.googleapis.com/auth/userinfo.email " + \
                "https://www.googleapis.com/auth/userinfo.profile" 
        redirect_uri = settings.BASE_BACKEND_URL + "/google/callback" 
        google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth" 
        url = f"{google_auth_api}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}" 
        return Response(data={"url":url}, status=status.HTTP_200_OK)

class GoogleSigninCallBackApi(APIView):
    def social_user_login(self, user, data): #jwt_login()
        login(self.request, user, 'user.googleapi.GoogleBackend')  # GoogleBackend 를 통한 인증 시도
        serializer = UserSocialLoginSerializer(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.execute()

        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @transaction.atomic
    def social_user_create(self, email, **extra_fields):
        data = copy.deepcopy(extra_fields)
        data["email"]=email
        data["password"]=settings.GOOGLE_PASSWORD

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
        summary="Google Login Callback",
        tags=['auth', ],
        responses={
            200: OpenApiResponse(response=UserSocialLoginSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def get(self, request, *args, **kwargs): 
        # code = request.GET.get('code') 
        # google_token_api = "https://oauth2.googleapis.com/token" 
        # access_token = google_get_access_token(google_token_api, code) 
        # user_data = google_get_user_info(access_token=access_token) # services.py method

        user_data = request.data
        profile_data = { 
            'email': user_data['email'],  #username->email
            'first_name': user_data.get('given_name', ''), 
            'last_name': user_data.get('family_name', ''), 
            'display_name': user_data.get('name', ''), 
            'path': "google", 
            'age':1, #왜 필수인가
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


