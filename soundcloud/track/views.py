from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from soundcloud.utils import CustomObjectPermissions
from track.models import Track
from track.serializers import SimpleTrackSerializer, TrackSerializer, TrackMediaUploadSerializer
from user.models import User
from user.serializers import SimpleUserSerializer

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
    )
)
class TrackViewSet(viewsets.ModelViewSet):

    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    permission_classes = (CustomObjectPermissions, )
    lookup_field = 'id'
    lookup_url_kwarg = 'track_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TrackMediaUploadSerializer
        if self.action in ['list']:
            return SimpleTrackSerializer
        if self.action in ['likers', 'reposters']:
            return SimpleUserSerializer
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ['likers', 'reposters']:
            self.track = getattr(self, 'track', None) or get_object_or_404(Track, id=self.kwargs[self.lookup_url_kwarg])

            if self.action == 'likers':
                return User.objects.prefetch_related('followers', 'owned_tracks').filter(likes__track=self.track)
            if self.action == 'reposters':
                return User.objects.prefetch_related('followers', 'owned_tracks').filter(reposts__track=self.track)
        if self.action in ['create', 'retrieve', 'update', 'partial_update']:
            return Track.objects.select_related('artist').prefetch_related('likes', 'reposts', 'comments', 'artist__followers', 'artist__owned_tracks')
        if self.action in ['list']:
            if self.request.user.is_authenticated:
                return Track.objects.exclude(~Q(artist=self.request.user), is_private=True).select_related('artist').prefetch_related('likes', 'reposts', 'comments', 'artist__followers', 'artist__owned_tracks')
            else:
                return Track.objects.exclude(is_private=True).select_related('artist').prefetch_related('likes', 'reposts', 'comments', 'artist__followers', 'artist__owned_tracks')
        else:
            return super().get_queryset()

    @action(detail=True)
    def likers(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def reposters(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
