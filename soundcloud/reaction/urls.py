from django.urls import path
from .views import LikeTrackAPIView, LikeSetAPIView, RepostSetAPIView, RepostTrackAPIView


urlpatterns = [
    path('likes/tracks/<str:track_id>', LikeTrackAPIView.as_view(), name='like-track'),  # /likes
    path('likes/sets/<str:set_id>', LikeSetAPIView.as_view(), name='like-set'),
    path('reposts/tracks/<str:track_id>', RepostTrackAPIView.as_view(), name='repost-track'),  # /reposts
    path('reposts/sets/<str:set_id>', RepostSetAPIView.as_view(), name='repost-set'),
]