from rest_framework import viewsets
from rest_framework.response import Response
from track.models import Track
from track.serializers import SimpleTrackSerializer, TrackSerializer, TrackUploadSerializer
from drf_spectacular.utils import OpenApiResponse, extend_schema


class TrackViewSet(viewsets.GenericViewSet):

    query_set = Track.objects.all()
    lookup_field = 'track_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return TrackUploadSerializer
        elif self.action in ['list']:
            return SimpleTrackSerializer
        else:
            return TrackSerializer

    @extend_schema(
        summary="Create Track",
        responses={
            201: OpenApiResponse(response=TrackUploadSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data, status = serializer.save()

        return Response(data=data, status=status)
