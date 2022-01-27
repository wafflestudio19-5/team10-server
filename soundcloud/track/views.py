from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from soundcloud.utils import CustomObjectPermissions
from track.models import Track
from track.schemas import tracks_viewset_schema
from track.serializers import SimpleTrackSerializer, TrackHitService, TrackSerializer, TrackMediaUploadSerializer
from user.models import User
from user.serializers import SimpleUserSerializer

@tracks_viewset_schema
class TrackViewSet(viewsets.ModelViewSet):

    permission_classes = (CustomObjectPermissions, )
    filter_backends = (OrderingFilter, )
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_url_kwarg = 'track_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TrackMediaUploadSerializer
        if self.action in ['list']:
            return SimpleTrackSerializer
        if self.action in ['likers', 'reposters']:
            return SimpleUserSerializer
        if self.action in  ['hit']:
            return TrackHitService

        return TrackSerializer

    def get_queryset(self):

        # hide private tracks in the queryset
        user = self.request.user if self.request.user.is_authenticated else None
        queryset = Track.objects \
            .exclude(~Q(artist=user) & Q(is_private=True)) \
            .prefetch_related('artist__followers', 'artist__owned_tracks')

        if self.action in ['likers', 'reposters']:
            self.track = getattr(self, 'track', None) or get_object_or_404(queryset, pk=self.kwargs[self.lookup_url_kwarg])

        querysets = {
            'likers': User.objects.filter(likes__track=self.track),
            'reposters': User.objects.filter(reposts__track=self.track),
        }

        return querysets.get(self.action) or queryset

    @action(detail=True)
    def likers(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def reposters(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['PUT'], permission_classes=(permissions.AllowAny, ))
    def hit(self, request, *args, **kwargs):
        track = self.get_object()
        service = self.get_serializer(track)
        status, data = service.execute()

        return Response(status=status, data=data)
