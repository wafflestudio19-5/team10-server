from django.contrib.auth import get_user_model, logout
from rest_framework import status, permissions, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveUpdateAPIView, get_object_or_404
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

    queryset = User.objects.all()
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
        if self.action in ['followers', 'followings', 'tracks', 'sets', 'likes_tracks', 'reposts_tracks', 'likes_sets', 'reposts_sets', 'history_tracks', 'history_sets', 'comments']:
            self.user = getattr(self, 'user', None) or get_object_or_404(User, id=self.kwargs[self.lookup_url_kwarg])

            if self.action == 'followers':
                return User.objects.filter(followings__followee=self.user)
            if self.action == 'followings':
                return User.objects.filter(followers__follower=self.user)
            if self.action == 'tracks':
                if self.request.user.is_authenticated and self.request.user == self.user:
                    return Track.objects.filter(artist=self.user)
                return Track.objects.exclude(is_private=True).filter(artist=self.user)
            if self.action == 'sets':
                if self.request.user.is_authenticated and self.request.user == self.user:
                    return Set.objects.filter(creator=self.user)
                return Set.objects.exclude(is_private=True).filter(creator=self.user)
            if self.action == 'likes_tracks':
                return Track.objects.prefetch_related('artist__followers', 'artist__owned_tracks').filter(likes__user=self.user)
            if self.action == 'reposts_tracks':
                return Track.objects.prefetch_related('artist__followers', 'artist__owned_tracks').filter(reposts__user=self.user)
            if self.action == 'likes_sets':
                return Set.objects.select_related('creator').prefetch_related('likes', 'reposts', 'tracks', 'tags', 'creator__followers', 'creator__owned_tracks').filter(likes__user=self.user)
            if self.action == 'reposts_sets':
                return Set.objects.select_related('creator').prefetch_related('likes', 'reposts', 'tracks', 'tags', 'creator__followers', 'creator__owned_tracks').filter(reposts__user=self.user)
            if self.action == 'history_tracks':
                return self.user.played_tracks.prefetch_related('artist__followers', 'artist__owned_tracks')
            if self.action == 'history_sets':
                return self.user.played_sets
            if self.action == 'comments':
                return Comment.objects.select_related('track').filter(writer=self.user)

        return super().get_queryset()

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

    @action(detail=True, url_path='history/tracks', ordering_fields=['trackhit__last_hit'], ordering=['-trackhit__last_hit'])
    def history_tracks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, url_path='history/sets', ordering_fields=['sethit__last_hit'], ordering=['-sethit__last_hit'])
    def history_sets(self, request, *args, **kwargs):
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

        return get_object_or_404(self.get_queryset(), id=self.request.user.id)


@users_follow_schema
class UserFollowView(GenericAPIView):

    serializer_class = UserFollowService
    queryset = User.objects.all()
    lookup_field = 'id'
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
