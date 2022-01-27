from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from comment.models import Comment
from comment.schemas import *
from comment.serializers import TrackCommentSerializer
from soundcloud.utils import CustomObjectPermissions
from track.models import Track


@comments_viewset_schema
class CommentViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):

    serializer_class = TrackCommentSerializer
    permission_classes = (CustomObjectPermissions, )
    lookup_url_kwarg = 'comment_id'
    filter_backends = (OrderingFilter, )
    ordering_fields = []
    ordering = ['-group__created_at', 'created_at']

    def get_queryset(self):
        
        # hide private tracks in the queryset
        user = self.request.user if self.request.user.is_authenticated else None
        track_queryset = Track.objects.exclude(~Q(artist=user) & Q(is_private=True))

        self.track = getattr(self, 'track', None) or get_object_or_404(track_queryset, id=self.kwargs['track_id'])

        if self.action in ['list']:
            res = Comment.objects\
                .select_related('writer')\
                .prefetch_related('writer__followers', 'writer__owned_tracks')\
                .filter(track=self.track)
        else:
            res = Comment.objects.filter(track=self.track)

        return res

    def get_serializer_context(self):
        context = super().get_serializer_context()

        # hide private tracks in the queryset
        user = self.request.user if self.request.user.is_authenticated else None
        track_queryset = Track.objects.exclude(~Q(artist=user) & Q(is_private=True))
        context['track'] = getattr(self, 'track', None) or get_object_or_404(track_queryset, id=self.kwargs['track_id'])

        return context

    def perform_destroy(self, instance):
        service = self.get_serializer(instance)
        service.delete()
