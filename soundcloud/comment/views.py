from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, extend_schema
from comment.serializers import *


class CommentViewSet(viewsets.GenericViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_object(self):
        multi_filter = {'id': self.kwargs['comment_id'], 'track__id': self.kwargs['track_id']}
        comment = get_object_or_404(self.queryset, **multi_filter)
        self.check_object_permissions(self.request, comment)
        return comment

    @extend_schema(
        summary="Create Comment",
        request=PostCommentService,
        responses={
            201: OpenApiResponse(description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
    def create(self, request, *args, **kwargs):
        service = PostCommentService(data=request.data, context={'request': request, 'track_id': self.kwargs['track_id']})
        status_code, data = service.execute()
        return Response(status=status_code, data=data)

    @extend_schema(
        summary="Delete Comment",
        responses={
            204: OpenApiResponse(description='No Content'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        service = DeleteCommentService(context={'request': request, 'comment': self.get_object()})
        status_code, data = service.execute()
        return Response(status=status_code, data=data)

    @extend_schema(
        summary="Get Comments on Track",
        responses={
            200: OpenApiResponse(response=CommentSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def list(self, request, *args, **kwargs):
        service = RetrieveCommentService(context={'track_id': self.kwargs['track_id']})
        status_code, data = service.execute()
        return Response(status=status_code, data=self.get_serializer(data, many=True).data)
