from rest_framework import viewsets
from soundcloud.utils import CustomObjectPermissions
from track.models import Track
from user.models import User
from reaction.models import Like, Repost
from track.serializers import SimpleTrackSerializer, TrackSerializer, TrackMediaUploadSerializer
from user.serializers import SimpleUserSerializer
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

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
    )
)
class TrackViewSet(viewsets.ModelViewSet):

    queryset = Track.objects.select_related('artist').prefetch_related('likes', 'reposts', 'comments', 'artist__followers', 'artist__owned_tracks')
    permission_classes = (CustomObjectPermissions, )
    lookup_field = 'id'
    lookup_url_kwarg = 'track_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TrackMediaUploadSerializer
        elif (self.action in ['list']) and (not self.detail):
            return SimpleTrackSerializer
        elif self.detail:
            return SimpleUserSerializer
        else:
            return TrackSerializer

    @action(methods=['GET'], detail=True)
    def likers(self, request, track_id=None):
        get_object_or_404(self.get_queryset(), id=track_id)

        like_qs = Like.objects.filter(track=track_id).select_related('user').values('user')
        queryset = User.objects.filter(id__in=like_qs)

        return Response(self.get_serializer(queryset, many=True).data)

    @action(methods=['GET'], detail=True)
    def reposters(self, request, track_id=None):
        get_object_or_404(self.get_queryset(), id=track_id)

        repost_qs = Repost.objects.filter(track=track_id).select_related('user').values('user')
        queryset = User.objects.filter(id__in=repost_qs)

        return Response(self.get_serializer(queryset, many=True).data)
