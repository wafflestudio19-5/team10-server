from django.db.models import F
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from comment.models import Comment
from comment.serializers import TrackCommentSerializer
from soundcloud.utils import CommentPagination, CustomObjectPermissions
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
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
)
class CommentViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):

    serializer_class = TrackCommentSerializer
    permission_classes = (CustomObjectPermissions, )
    lookup_field = 'id'
    lookup_url_kwarg = 'comment_id'
    # pagination_class = CommentPagination
    filter_backends = (OrderingFilter, )
    ordering_fields = []
    ordering = ['-group__created_at', 'created_at']

    def get_queryset(self):
        self.track = getattr(self, 'track', None) or get_object_or_404(Track, id=self.kwargs['track_id'])

        if self.action in ['list']:
            queryset = Comment.objects\
                .select_related('writer')\
                .prefetch_related('writer__followers', 'writer__owned_tracks')\
                .filter(track=self.track)\
                .annotate(group_created_at=F('group__created_at'))
        else:
            queryset = Comment.objects.filter(track=self.track)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['track'] = getattr(self, 'track', None) or get_object_or_404(Track, id=self.kwargs['track_id'])

        return context

    def perform_destroy(self, instance):
        service = self.get_serializer(instance)
        service.delete()
