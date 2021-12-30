from django.urls import path, include
from rest_framework.routers import SimpleRouter
from set.views import *

router = SimpleRouter(trailing_slash=False)
router.register('sets', SetViewSet, basename='sets')   # /sets

urlpatterns = [
    path('', include(router.urls))
]
