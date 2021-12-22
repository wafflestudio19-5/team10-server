from rest_framework import viewsets
from rest_framework.response import Response
from track.models import Track
from track.serializers import TrackSerializer, TrackPresignedURLSerializer
from drf_spectacular.utils import OpenApiResponse, extend_schema


class TrackViewSet(viewsets.GenericViewSet):

    serializer_class = TrackSerializer
    query_set = Track.objects.all()
    lookup_field = 'track_id'

    @extend_schema(
        summary="Create Track",
        request={
            'application/json': serializer_class,
            'application/x-www-form-urlencoded': serializer_class,
        },
        responses={
            201: OpenApiResponse(response=TrackPresignedURLSerializer, description='Created'),
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
