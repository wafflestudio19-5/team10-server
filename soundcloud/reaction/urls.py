from django.urls import path
from .views import LikeTrackAPIView, LikeSetAPIView


urlpatterns = [
    path('likes/tracks/<str:pk>', LikeTrackAPIView.as_view(), name='like-track'),  # /likes
    path('likes/sets/<str:pk>', LikeSetAPIView.as_view(), name='like-set'),
    # path('reposts/tracks/<int:pk>', RepostTrackAPIView.as_view(), name='repost-track'),  # /reposts
    # path('reposts/sets/<int:pk>', RepostSetAPIView.as_view(), name='repost-set'),
]