from django.urls import path, include
from rest_framework.routers import SimpleRouter
from track.views import TrackViewSet, TrackSearchAPIView

router = SimpleRouter(trailing_slash=False)
router.register('tracks', TrackViewSet, basename='tracks')

urlpatterns = [
    path('', include(router.urls)),
    path('search/tracks', TrackSearchAPIView.as_view(), name='search-tracks'),
]
