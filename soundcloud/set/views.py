from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from set.models import Set
from set.schemas import *
from set.serializers import *
from soundcloud.utils import CustomObjectPermissions
from user.models import User


@sets_viewset_schema
class SetViewSet(viewsets.ModelViewSet):

    permission_classes = (CustomObjectPermissions, )
    filter_backends = (OrderingFilter, )
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_url_kwarg = 'set_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SetMediaUploadSerializer
        if self.action in ['likers', 'reposters']:
            return SimpleUserSerializer
        if self.action in ['list']:
            return SimpleSetSerializer

        return SetSerializer

    def get_queryset(self):

        # hide private sets in the queryset
        user = self.request.user if self.request.user.is_authenticated else None
        queryset = Set.objects.exclude(~Q(creator=user) & Q(is_private=True))

        if self.action in ['likers', 'reposters']:
            self.set = getattr(self, 'set', None) or get_object_or_404(queryset, id=self.kwargs[self.lookup_url_kwarg])
            querysets = {
                'likers': User.objects.filter(likes__set=self.set),
                'reposters': User.objects.filter(reposts__set=self.set),
            }
            return querysets.get(self.action)

        return queryset
    
    # 1. POST /sets/ - 빈 playlist 생성 - mixin 이용
    # 2. PUT /sets/{set_id} - mixin 이용
    # 3. GET /sets/{set_id} - mixin 이용
    # 4. DELETE /sets/{set_id} - mixin 이용

    # 5. GET /sets/{set_id}/likers
    @action(detail=True)
    def likers(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # 6. GET /sets/{set_id}/reposters
    @action(detail=True)
    def reposters(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@sets_track_schema
class SetTrackViewSet(viewsets.GenericViewSet): 
    permission_classes = (CustomObjectPermissions, )
    lookup_url_kwarg = 'set_id'
    serializer_class = SetTrackService
    queryset = Set.objects.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['set'] = self.get_object()
        track_ids = self.request.data.get('track_ids')
        context['track_ids'] = track_ids
        return context

    
    # 7. POST /sets/{set_id}/tracks (add track to playlist)
    # 8. DELETE /sets/{set_id}/tracks (remove track from playlist)
    @action(methods=['POST', 'DELETE'], detail=True)
    def tracks(self, request, *args, **kwargs):
        service = self.get_serializer()
        if request.method == 'POST':
            return self._add(service)
        else:
            return self._remove(service)

    def _add(self, service):
        status, data = service.create()
        return Response(status=status, data=data)

    def _remove(self, service):
        status, data = service.delete()
        return Response(status=status, data=data)
