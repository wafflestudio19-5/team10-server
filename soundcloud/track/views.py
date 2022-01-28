from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from drf_haystack.viewsets import HaystackGenericAPIView, HaystackViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from soundcloud.utils import CustomObjectPermissions
from track.models import Track
from track.serializers import SimpleTrackSerializer, TrackHitService, TrackSerializer, TrackMediaUploadSerializer, TrackSearchSerializer
from track.schemas import tracks_viewset_schema
from user.models import User
from user.serializers import SimpleUserSerializer
from datetime import datetime

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
        if self.action in ['hit']:
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
            return querysets.get(self.action)

        return queryset

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


class TrackSearchAPIView(ListModelMixin, HaystackGenericAPIView):
    index_models = [Track]
    serializer_class = TrackSearchSerializer

    def get_queryset(self, index_models=[]):
        queryset = self.object_class()._clone()
        queryset = queryset.models(*self.index_models)

        ids = self.request.GET.getlist('ids[]', None)
        genres = self.request.GET.getlist('genres[]', None)
        start = self.request.GET.get('created_at[from]', None)
        end = self.request.GET.get('created_at[to]', None)

        q = Q()

        if ids:
            q &= Q(id__in=ids)
        if genres:
            q &= Q(genre_name__in=genres)
        if start:
            q &= Q(pub_date__gte=datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ'))
        if end:
            q &= Q(pub_date__lte=datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ'))

        if self.request.user.is_authenticated:
            queryset = queryset.exclude(~Q(artist=self.request.user), is_private=True)
        else:
            queryset = queryset.exclude(is_private=True)

        return queryset.filter(q)

    @extend_schema(
        summary="Search",
        responses={
            200: OpenApiResponse(response=TrackSearchSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
