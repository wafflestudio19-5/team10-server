from rest_framework import viewsets
from track.models import Track
from track.serializers import SimpleTrackSerializer, TrackSerializer, TrackUploadSerializer
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view


@extend_schema_view(
    create=extend_schema(
        summary="Create Track",
        responses={
            '201': OpenApiResponse(response=TrackUploadSerializer, description='Created'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '409': OpenApiResponse(description='Conflict'),
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
            '200': OpenApiResponse(response=TrackUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
            '409': OpenApiResponse(description='Conflict'),
        }
    ),
    partial_update=extend_schema(
        summary="Partial Update Track",
        responses={
            '200': OpenApiResponse(response=TrackUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
            '409': OpenApiResponse(description='Conflict'),
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
            '200': OpenApiResponse(response=TrackSerializer, description='OK'),
        }
    )
)
class TrackViewSet(viewsets.ModelViewSet):

    queryset = Track.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'track_id'

    def get_serializer_class(self):
        if self.action in ['retrieve', 'delete']:
            return TrackSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TrackUploadSerializer
        elif self.action in ['list']:
            return SimpleTrackSerializer


    # TODO: 자기 트랙만 수정하게
    # TODO: 409 에러 핸들링
