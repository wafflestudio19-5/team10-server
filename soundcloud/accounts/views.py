from django.conf import settings
from user.models import User
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
import requests
from rest_framework import status,permissions
from json.decoder import JSONDecodeError
from django.shortcuts import redirect


# google_login 실행 후 로그인 성공 시, Callback 함수로 Code 값 전달받음
# 받은 Code로 Google에 Access Token 요청
# Access Token으로 Email 값을 Google에게 요청
# 전달받은 Email, Access Token, Code를 바탕으로 회원가입/로그인 진행

state = getattr(settings, 'STATE')
BASE_URL = 'http://localhost:8000/'
#BASE_URL = 'https://www.soundwaffle.com/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/login/callback/'

def google_login(request):
    permission_classes = (permissions.AllowAny, )
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")
    # 이 함수와 매핑된 url로 들어가면, client_id, redirect uri 등과 같은 정보를 url parameter로 함께 보내 리다이렉트한다. 
    # 그러면 구글 로그인 창이 뜨고, 알맞은 아이디, 비밀번호로 진행하면 Callback URI로 Code값이 들어가게 된다.


def google_callback(request):
    permission_classes = (permissions.AllowAny, )
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')
    """
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    print("access_token="+access_token)
    # Google API Server에 응답받은 Code, client_secret, state와 같은 url parameter를 함께 Post 요청을 보낸다. 
    # 문제없이 성공하면, access_token을 가져올 수 있다.


    """
    Email Request
    """
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    # 응답받은 Access Token을 로그인된 사용자의 Email을 응답받기 위해 url parameter에 포함하여 요청 
    # - Access Token이 틀렸거나, 에러 발생으로 200 OK 코드를 응답받지 못하면 400으로 Response

    """
    **Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None: #일반계정
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google': #다른 provider(SNS)로 가입한 계정
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저 - 로그인 진행
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
        # 1. 전달받은 email과 동일한 Email이 있는지 찾아본다.
        # 2-1. 만약 있다면?
        #        - FK로 연결되어있는 socialaccount 테이블에서 이메일의 유저가 있는지 체크
        #        - 없으면 일반 계정이므로, 에러 메세지와 함께 400 리턴
        #        - 있지만 다른 Provider로 가입되어 있으면 에러 메세지와 함께 400 리턴
        #        - 위 두개에 걸리지 않으면 로그인 진행, 해당 유저의 JWT 발급, 그러나 도중에          
        #          예기치 못한 오류가 발생하면 에러 메세지와 함께 오류 Status 응답
        # 2-2. 없다면 (신규 유저이면)
        #        - 회원가입 진행 및 해당 유저의 JWT 발급
        #        - 그러나 도중에 예기치 못한 오류가 발생하면 에러 메세지와 함께 오류 Status응답

class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client