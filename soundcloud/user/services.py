from django.conf import settings 
from django.core.exceptions import ValidationError 
from soundcloud.settings.common import *
import requests

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token' 
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def google_get_access_token(google_token_api, code): #성공해서 받은 code를 가지고 access_token을 
    client_id = get_secret("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = get_secret("SOCIAL_AUTH_GOOGLE_SECRET")
    code = code 
    grant_type = 'authorization_code' 
    redirection_uri = settings.BASE_BACKEND_URL + "/api/v1/auth/login/google/callback" 
    state = "random_string"

    google_token_api += f"?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type={grant_type}&redirect_uri={redirection_uri}&state={state}" 
        
    token_response = requests.post(google_token_api) 
    if not token_response.ok: 
        raise ValidationError('google_token is invalid') 
    access_token = token_response.json().get('access_token')

    return access_token

def google_get_user_info(access_token): #access_token을 통해서 유저 정보를 가져오기
    user_info_response = requests.get( 
        "https://www.googleapis.com/oauth2/v3/userinfo", 
        params={ 
            'access_token': access_token 
        } 
    ) 
    if not user_info_response.ok: 
        raise ValidationError('Failed to obtain user info from Google.') 
    user_info = user_info_response.json() 
    return user_info

