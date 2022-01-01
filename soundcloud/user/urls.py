from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserSelfView, UserLoginView, UserSignUpView, UserLogoutView, UserViewSet, UserFollowView

router = SimpleRouter(trailing_slash=False)
router.register('users', UserViewSet, basename='users')         # /users

urlpatterns = [
    path('signup', UserSignUpView.as_view(), name='signup'),    # /signup
    path('login', UserLoginView.as_view(), name='login'),       # /login
    path('logout', UserLogoutView.as_view(), name='logout'),    # /logout
    path('users/me/followings/<int:user_id>', UserFollowView.as_view(), name='user-follow'),  # /users/me/followings/{user_id}
    path('users/me', UserSelfView.as_view(), name='user-self'), # /users/me
    path('', include(router.urls), name='user'),                # /users/{user_id}
]