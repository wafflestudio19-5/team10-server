from django.urls import path, include
from rest_framework.routers import SimpleRouter
from track.views import CommentView

urlpatterns = [
    path('tracks/<int:track_id>/comments', CommentView.as_view(), name='comment'),
]
