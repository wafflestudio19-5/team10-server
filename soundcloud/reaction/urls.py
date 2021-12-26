from django.urls import path
from .views import LikeTrackView, LikeSetView, RepostTrackView, RepostSetView


urlpatterns = [
    path('likes/tracks/<str:track_id>', LikeTrackView.as_view(), name='like-track'),  # /likes
    path('likes/sets/<str:set_id>', LikeSetView.as_view(), name='like-set'),
    path('reposts/tracks/<str:track_id>', RepostTrackView.as_view(), name='repost-track'),  # /reposts
    path('reposts/sets/<str:set_id>', RepostSetView.as_view(), name='repost-set'),
]