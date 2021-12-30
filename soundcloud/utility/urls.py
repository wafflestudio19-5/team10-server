from django.urls import path
from .views import ResolveView


urlpatterns = [
    path('resolve', ResolveView.as_view(), name='resolve'),  # /resolve
]
