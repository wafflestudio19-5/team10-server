from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from user.services import google_get_access_token, google_get_user_info
from user.views import *
from soundcloud.settings.common import *
from django.db import transaction
import copy

User = get_user_model()

class GoogleLoginApi(PermissionsMixin, APIView):
    def get(self, request, *args, **kwargs): 
        client_id = get_secret("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        scope = "https://www.googleapis.com/auth/userinfo.email " + \
                "https://www.googleapis.com/auth/userinfo.profile" 
        redirect_uri = settings.BASE_BACKEND_URL + "/google/callback" 
        google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth" 
        response = redirect( 
            f"{google_auth_api}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}" 
            ) 
            
        return response

class GoogleSigninCallBackApi(PermissionsMixin, APIView):
    permission_classes = (permissions.AllowAny, )

    def social_user_login(response, user): #jwt_login()
        return response
        
    @transaction.atomic
    def social_user_create(self, email, **extra_fields):
        data = copy.deepcopy(extra_fields)
        data["email"]=email
        data["password"]="googlepassword"

        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return user

    @transaction.atomic
    def social_user_get_or_create(self, email, **extra_data):
        data = copy.deepcopy(extra_data)
        data["email"]=email

        if User.objects.filter(email=email).exists(): #이미 존재하는 이메일이면 로그인 비번은 첫 시도시 unusable로 설정된 상태.
            user = User.objects.filter(email=email).first()
            response = redirect(settings.BASE_FRONTEND_URL)
            response = self.social_user_login(response=response, user=user)

            return response
                

        user = self.social_user_create(email=email, **extra_data)
        response = redirect(settings.BASE_FRONTEND_URL)
        response = self.social_user_login(response=response, user=user)

        return response


    def get(self, request, *args, **kwargs): 
        code = request.GET.get('code') 
        google_token_api = "https://oauth2.googleapis.com/token" 
        access_token = google_get_access_token(google_token_api, code) 
        user_data = google_get_user_info(access_token=access_token) # services.py method
        profile_data = { 
            'email': user_data['email'],  #username->email
            'first_name': user_data.get('given_name', ''), 
            'last_name': user_data.get('family_name', ''), 
            'nickname': user_data.get('nickname', ''), 
            'display_name': user_data.get('name', ''), 
            #'image': user_data.get('picture', None), 
            'path': "google", 
            'age':1, #왜 필수인가
            }  #구글이 넘겨주는 거.

        #response = redirect(settings.BASE_FRONTEND_URL) 
        #response = jwt_login(response=response, user=user)  # user 에 맞게 수정하기
        
        return self.social_user_get_or_create(**profile_data) 





