from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from track.models import Track
from track.serializers import CommentSerializer, PostCommentService, DeleteCommentService, RetrieveCommentService


class CommentView(GenericAPIView):

    serializer_class = CommentSerializer
    queryset = Track.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'track_id'

    @extend_schema(
        summary="Create Comment",
        responses={
            201: OpenApiResponse(description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
    def post(self, request, *args, **kwargs):
        service = PostCommentService(data=request.data, context={'request': request, 'track': self.get_object()})
        status_code, data = service.execute()
        return Response(status=status_code, data=data)

    @extend_schema(
        summary="Delete Comment",
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def delete(self, request, *args, **kwargs):
        service = DeleteCommentService(data=request.data, context={'request': request, 'track': self.get_object()})
        status_code, data = service.execute()
        return Response(status=status_code, data=data)

    @extend_schema(
        summary="Get Comments on Track",
        responses={
            200: OpenApiResponse(response=CommentSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def get(self, request, *args, **kwargs):
        service = RetrieveCommentService(context={'track': self.get_object()})
        status_code, data = service.execute()
        return Response(status=status_code, data=self.get_serializer(data, many=True).data)
