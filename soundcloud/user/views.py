from django.contrib.auth import get_user_model, logout
from django.db.models import F
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
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
from user.serializers import *

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary="Signup",
        tags=['auth', ],
        responses={
            201: OpenApiResponse(response=UserCreateSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
)
class UserSignUpView(CreateAPIView):

    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )


class UserLoginView(GenericAPIView):

    serializer_class = UserLoginSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )

    @extend_schema(
        summary="Login",
        tags=['auth', ],
        responses={
            200: OpenApiResponse(response=UserLoginSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.execute()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):

    @extend_schema(
        summary="Logout",
        tags=['auth', ],
        description="Do nothing, actually.",
        responses={
            200: OpenApiResponse(description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    )
    def post(self, request):
        logout(request)
        
        return Response({"You\'ve been logged out"}, status=status.HTTP_200_OK)

      
@extend_schema_view(
    retrieve=extend_schema(
        summary="Retrieve User",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    list=extend_schema(
        summary="List Users",
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer, description='OK'),
        }
    ),
    followers=extend_schema(
        summary="Get User's Followers",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    followings=extend_schema(
        summary="Get User's Followings",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    tracks=extend_schema(
        summary="Get User's Tracks",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=UserTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    sets=extend_schema(
        summary="Get User's sets",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    history_tracks=extend_schema(
        summary="Get User's Track History",
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    history_sets=extend_schema(
        summary="Get User's Set History",
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    likes_tracks=extend_schema(
        summary="Get User's Liked Tracks",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    reposts_tracks=extend_schema(
        summary="Get User's Reposted Tracks",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    comments=extend_schema(
        summary="Get User's Comments",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=UserCommentSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'
    filter_backends = (OrderingFilter, )
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in [ 'list', 'followers', 'followings' ]:
            return SimpleUserSerializer
        if self.action in [ 'tracks' ]:
            return UserTrackSerializer
        if self.action in [ 'likes_tracks', 'reposts_tracks', 'history_tracks' ]:
            return SimpleTrackSerializer
        if self.action in  [ 'history_sets', 'sets' ]:
            return SimpleSetSerializer
        if self.action in [ 'comments' ]:
            return UserCommentSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ['followers', 'followings', 'tracks', 'sets', 'likes_tracks', 'reposts_tracks', 'history_tracks', 'history_sets', 'comments']:
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

    @action(detail=True)
    def comments(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Me",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    put=extend_schema(
        summary="Update Me",
        responses={
            200: OpenApiResponse(response=UserMediaUploadSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    patch=extend_schema(
        summary="Partial Update Me",
        responses={
            200: OpenApiResponse(response=UserMediaUploadSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
)
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


class UserFollowView(GenericAPIView):

    serializer_class = UserFollowService
    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.get_object()

        return context

    @extend_schema(
        summary="Follow User",
        responses={
            201: OpenApiResponse(description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def post(self, request, *args, **kwargs):
        service = self.get_serializer()
        status, data = service.create()

        return Response(status=status, data=data)

    @extend_schema(
        summary="Unfollow User",
        responses={
            204: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def delete(self, request, *args, **kwargs):
        service = self.get_serializer()
        status, data = service.delete()

        return Response(status=status, data=data)
