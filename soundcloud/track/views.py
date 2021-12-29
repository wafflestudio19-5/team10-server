from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from track.models import Track
from track.serializers import CommentSerializer, CommentService


class CommentView(GenericAPIView):

    serializer_class = CommentSerializer
    queryset = Track.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'track_id'

    def post(self, request, *args, **kwargs):
        service = CommentService(data=request.data, context={'request': request, 'track': self.get_object()})
        status_code, data = service.post()
        return Response(status=status_code, data=data)

    def delete(self, request, *args, **kwargs):
        service = CommentService(context={'request': request, 'track': self.get_object()})
        status_code, data = service.delete()
        return Response(status=status_code, data=data)

    def get(self, request, *args, **kwargs):
        service = CommentService(context={'track': self.get_object()})
        status_code, data = service.retrieve()
        return Response(status=status_code, data=self.get_serializer(data, many=True).data)
