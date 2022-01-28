from django.contrib.auth import get_user_model, logout
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from drf_haystack.viewsets import HaystackGenericAPIView
from rest_framework import status, permissions, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from comment.models import Comment
from comment.serializers import UserCommentSerializer
from set.models import Set
from set.serializers import SimpleSetSerializer
from track.serializers import SimpleTrackSerializer, UserTrackSerializer
from user.schemas import *
from user.serializers import *
from datetime import datetime

User = get_user_model()

@auth_signup_schema
class UserSignUpView(CreateAPIView):

    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )


@auth_login_schema
class UserLoginView(GenericAPIView):

    serializer_class = UserLoginSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.execute()

        return Response(serializer.data, status=status.HTTP_200_OK)


@auth_logout_schema
class UserLogoutView(APIView):

    def post(self, request):
        logout(request)
        
        return Response({"You\'ve been logged out"}, status=status.HTTP_200_OK)


@users_viewset_schema
class UserViewSet(viewsets.ReadOnlyModelViewSet):

    lookup_url_kwarg = 'user_id'
    filter_backends = (OrderingFilter, )
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['list', 'followers', 'followings']:
            return SimpleUserSerializer
        if self.action in ['tracks']:
            return UserTrackSerializer
        if self.action in ['likes_tracks', 'reposts_tracks', 'history_tracks']:
            return SimpleTrackSerializer
        if self.action in ['likes_sets', 'reposts_sets', 'history_sets', 'sets']:
            return SimpleSetSerializer
        if self.action in ['comments']:
            return UserCommentSerializer

        return UserSerializer

    def get_queryset(self):
        if self.action in ['retrieve', 'list']:
            return User.objects.all()

        self.user = getattr(self, 'user', None) or get_object_or_404(User, pk=self.kwargs[self.lookup_url_kwarg])
        
        # hide private tracks in the queryset
        request_user = self.request.user if self.request.user.is_authenticated else None
        track_queryset = Track.objects \
            .exclude(~Q(artist=request_user) & Q(is_private=True)) \
            .prefetch_related('artist__followers', 'artist__owned_tracks')

        # hide private sets in the queryset
        set_queryset = Set.objects \
            .exclude(~Q(creator=request_user) & Q(is_private=True)) \

        # hide comments of the private tracks in the queryset
        comment_queryset = Comment.objects \
            .exclude(~Q(track__artist=request_user) & Q(track__is_private=True))

        querysets = {
            'followers': User.objects.filter(followings__followee=self.user),
            'followings': User.objects.filter(followers__follower=self.user),
            'tracks': track_queryset.filter(artist=self.user),
            'sets': set_queryset.filter(creator=self.user),
            'likes_tracks': track_queryset.filter(likes__user=self.user),
            'reposts_tracks': track_queryset.filter(reposts__user=self.user),
            'likes_sets': set_queryset.filter(likes__user=self.user),
            'reposts_sets': set_queryset.filter(reposts__user=self.user),
            'history_tracks': track_queryset.filter(players=self.user),
            'history_sets': set_queryset.filter(players=self.user),
            'comments': comment_queryset.filter(writer=self.user),
        }

        if self.action in querysets:
            return querysets.get(self.action)
        else:
            return User.objects.all()

    @action(detail=True)
    def followers(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def followings(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def tracks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def sets(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='likes/tracks')
    def likes_tracks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='reposts/tracks')
    def reposts_tracks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='likes/sets')
    def likes_sets(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='reposts/sets')
    def reposts_sets(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='history/tracks', ordering_fields=['trackhit__last_hit'], ordering=['-trackhit__last_hit'])
    def history_tracks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='history/sets', ordering_fields=['sethit__last_hit'], ordering=['-sethit__last_hit'])
    def history_sets(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def comments(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@users_self_schema
class UserSelfView(RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method in [ 'PUT', 'PATCH' ]:
            return UserMediaUploadSerializer
        else:
            return super().get_serializer_class()

    def get_object(self):

        return get_object_or_404(self.get_queryset(), pk=self.request.user.id)


@users_follow_schema
class UserFollowView(GenericAPIView):

    serializer_class = UserFollowService
    queryset = User.objects.all()
    lookup_url_kwarg = 'user_id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.get_object()

        return context

    def post(self, request, *args, **kwargs):
        service = self.get_serializer()
        status, data = service.create()

        return Response(status=status, data=data)

    def delete(self, request, *args, **kwargs):
        service = self.get_serializer()
        status, data = service.delete()

        return Response(status=status, data=data)


class UserSearchAPIView(ListModelMixin, HaystackGenericAPIView):
    index_models = [User]
    serializer_class = UserSearchSerializer

    def get_queryset(self, index_models=[]):
        queryset = self.object_class()._clone()
        queryset = queryset.models(*self.index_models)

        ids = self.request.data.get('ids', None)
        location = self.request.data.get('location', None)

        q = Q()

        if ids:
            q &= Q(id__in=ids)
        if location:
            q &= Q(city__in=location) | Q(country__in=location)
        return queryset.filter(q)

    @extend_schema(
        summary="Search",
        responses={
            200: OpenApiResponse(response=UserSearchSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

