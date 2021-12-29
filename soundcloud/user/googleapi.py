from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from user.services import google_get_access_token, google_get_user_info
from user.views import *



User = get_user_model()

class GoogleLoginApi(PermissionsMixin, APIView):
    def get(self, request, *args, **kwargs): 
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
        scope = "https://www.googleapis.com/auth/userinfo.email " + \
                "https://www.googleapis.com/auth/userinfo.profile" 
        redirect_uri = settings.BASE_BACKEND_URL + "/google/callback" 
        google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth" 
        response = redirect( 
            f"{google_auth_api}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}" 
            ) 
            
        return response

class GoogleSigninCallBackApi(PermissionsMixin, APIView):
    def get(self, request, *args, **kwargs): 
        code = request.GET.get('code') 
        google_token_api = "https://oauth2.googleapis.com/token" 
        access_token = google_get_access_token(google_token_api, code) 
        user_data = google_get_user_info(access_token=access_token) # services.py method
        profile_data = { 
            'username': user_data['email'], 
            'first_name': user_data.get('given_name', ''), 
            'last_name': user_data.get('family_name', ''), 
            'nickname': user_data.get('nickname', ''), 
            'name': user_data.get('name', ''), 
            #'image': user_data.get('picture', None), 
            'path': "google", 
            }  #구글이 넘겨주는 거.
        user, _ = user_get_or_create(**profile_data)  # user 에 맞게 수정하기
        response = redirect(settings.BASE_FRONTEND_URL) 
        response = jwt_login(response=response, user=user)  # user 에 맞게 수정하기
        
        return response


    
