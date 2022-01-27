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
from user.models import User
from user.serializers import SimpleUserSerializer
from datetime import datetime

@extend_schema_view(
    create=extend_schema(
        summary="Create Track",
        responses={
            '201': OpenApiResponse(response=TrackMediaUploadSerializer, description='Created'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve Track",
        responses={
            '200': OpenApiResponse(response=TrackSerializer, description='OK'),
            '404': OpenApiResponse(description='Not Found')
        }
    ),
    update=extend_schema(
        summary="Update Track",
        responses={
            '200': OpenApiResponse(response=TrackMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    partial_update=extend_schema(
        summary="Partial Update Track",
        responses={
            '200': OpenApiResponse(response=TrackMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    destroy=extend_schema(
        summary="Delete Track",
        responses={
            '204': OpenApiResponse(description='No Content'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    list=extend_schema(
        summary="List Tracks",
        responses={
            '200': OpenApiResponse(response=SimpleTrackSerializer, description='OK'),
        }
    ),
    likers=extend_schema(
        summary="Get Track's Likers",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    reposters=extend_schema(
        summary="Get Track's Reposters",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    hit=extend_schema(
        summary="Hit Track",
        parameters=[
            OpenApiParameter("set_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A set id containing the track.'),
        ],
        responses={
            '200': OpenApiResponse(description='OK'),
        }
    )
)
class TrackViewSet(viewsets.ModelViewSet):

    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    permission_classes = (CustomObjectPermissions, )
    filter_backends = (OrderingFilter, )
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_field = 'id'
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
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ['likers', 'reposters']:
            self.track = getattr(self, 'track', None) or get_object_or_404(Track, id=self.kwargs[self.lookup_url_kwarg])

            if self.action == 'likers':
                return User.objects.filter(likes__track=self.track)
            if self.action == 'reposters':
                return User.objects.filter(reposts__track=self.track)
        if self.action in ['create', 'retrieve', 'update', 'partial_update']:
            return Track.objects.prefetch_related('artist__followers', 'artist__owned_tracks')
        if self.action in ['list']:
            if self.request.user.is_authenticated:
                return Track.objects.exclude(~Q(artist=self.request.user), is_private=True).prefetch_related('artist__followers', 'artist__owned_tracks')
            else:
                return Track.objects.exclude(is_private=True).prefetch_related('artist__followers', 'artist__owned_tracks')
        else:
            return super().get_queryset()

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
    pagination_class = None

    def get_queryset(self, index_models=[]):
        queryset = self.object_class()._clone()
        queryset = queryset.models(*self.index_models)

        ids = self.request.data.get('ids', None)
        genres = self.request.data.get('genres', None)
        created_at = self.request.data.get('created_at', None)

        q = Q()

        if ids:
            q &= Q(id__in=ids)
        if genres:
            q &= Q(genre__in=genres)
        if created_at:
            start = created_at.get('from', None)
            end = created_at.get('to', None)
            if start:
                q &= Q(pub_date__gte=datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ'))
            if end:
                q &= Q(pub_date__lte=datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ'))

        if self.request.user.is_authenticated:
            queryset = queryset.exclude(~Q(artist=self.request.user), is_private=True)
        else:
            queryset = queryset.exclude(is_private=True)

        return queryset.filter(q)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
