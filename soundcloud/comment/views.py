from rest_framework import viewsets, mixins
from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from comment.models import Comment
from comment.serializers import TrackCommentSerializer
from track.models import Track

@extend_schema_view(
    create=extend_schema(
        summary="Create Comment",
        responses={
            201: OpenApiResponse(response=TrackCommentSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    list=extend_schema(
        summary="Get Comments on Track",
        responses={
            200: OpenApiResponse(response=TrackCommentSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    destroy=extend_schema(
        summary="Delete Comment",
        responses={
            204: OpenApiResponse(description='No Content'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
)
class CommentViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = TrackCommentSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        self.track = getattr(self, 'track', None) or get_object_or_404(Track, id=self.kwargs['track_id'])

        return Comment.objects.filter(track=self.track).select_related('writer').prefetch_related('writer__followers', 'writer__owned_tracks')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['queryset'] = self.get_queryset()
        context['track'] = getattr(self, 'track', None)

        return context

    def perform_destroy(self, instance):
        service = self.get_serializer(instance)
        service.delete()
