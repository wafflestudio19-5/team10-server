from django.urls import path, include
from rest_framework.routers import SimpleRouter
from track.views import CommentViewSet

comment_simple = CommentViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
comment_detail = CommentViewSet.as_view({
    'delete': 'destroy',
})

urlpatterns = [
    path('tracks/<int:track_id>/comments', comment_simple),
    path('tracks/<int:track_id>/comments/<int:comment_id>', comment_detail),
]
