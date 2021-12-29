from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserLoginView, UserSignUpView, UserLogoutView, UserViewSet
from .googleapi import *

router = SimpleRouter(trailing_slash=False)
router.register('users', UserViewSet, basename='users')  # /users

urlpatterns = [
    path('signup', UserSignUpView.as_view(), name='signup'),  # /signup
    path('login', UserLoginView.as_view(), name='login'),  # /login
    path('logout', UserLogoutView.as_view(), name='logout'),  # /logout
    path('', include(router.urls), name='auth-user'),
    
    path('google', GoogleLoginApi.as_view(), name='google_login'),
    path('google/callback', GoogleSigninCallBackApi.as_view(), name='google_login_callback'),

]