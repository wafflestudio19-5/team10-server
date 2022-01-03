from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView
from rest_framework.response import Response
from set.models import Set
from track.models import Track
from user.models import User
from reaction.models import Like, Repost
from .serializers import LikeService, RepostService
from user.serializers import SimpleUserSerializer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view


class BaseReactionView(GenericAPIView):

    serializer_class = None
    queryset = None
    lookup_field = 'id'
    lookup_url_kwarg = None

    def get_serializer_context(self):
        context = super(BaseReactionView, self).get_serializer_context()
        context['target'] = self.get_object()

        return context

    def post(self, request, *args, **kwargs):
        service = self.get_serializer()
        status, data = service.create()

        return Response(status=status, data=data)

    def delete(self, request, *args, **kwargs):
        service = self.get_serializer()
        status, data = service.delete()

        return Response(status=status, data=data)


class LikeTrackView(BaseReactionView):

    serializer_class = LikeService
    queryset = Track.objects.all()
    lookup_url_kwarg = 'track_id'


class LikeSetView(BaseReactionView):

    serializer_class = LikeService
    queryset = Set.objects.all()
    lookup_url_kwarg = 'set_id'


class RepostTrackView(BaseReactionView):

    serializer_class = RepostService
    queryset = Track.objects.all()
    lookup_url_kwarg = 'track_id'


class RepostSetView(BaseReactionView):

    serializer_class = RepostService
    queryset = Set.objects.all()
    lookup_url_kwarg = 'set_id'


class BaseListView(ListAPIView):

    serializer_class = None
    queryset = None
    lookup_field = 'id'
    lookup_url_kwarg = 'track_id'


class LikeView(BaseListView):

    serializer_class = SimpleUserSerializer

    def get_queryset(self):
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        track = get_object_or_404(Track.objects.all(), **filter_kwargs)

        like_qs = Like.objects.filter(object_id=track.id).values('user_id')
        queryset = User.objects.filter(id__in=like_qs)

        return queryset

    @extend_schema(
        summary="Get Track's Likers",
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RepostView(BaseListView):

    serializer_class = SimpleUserSerializer

    def get_queryset(self):
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        track = get_object_or_404(Track.objects.all(), **filter_kwargs)

        repost_qs = Repost.objects.filter(object_id=track.id).values('user_id')
        queryset = User.objects.filter(id__in=repost_qs)

        return queryset

    @extend_schema(
        summary="Get Track's Reposters",
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
