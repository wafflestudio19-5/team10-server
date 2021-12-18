from django.utils.translation import override
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from track.models import Track
from track.serializers import TrackSerializer


class TrackViewSet(viewsets.GenericViewSet):

    serializer_class = TrackSerializer
    query_set = Track.objects.all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'delete'):
            permission_classes = (permissions.IsAuthenticated, )
        else:
            permission_classes = (permissions.AllowAny, )
        
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data, status = serializer.save()

        return Response(data=data, status=status)
