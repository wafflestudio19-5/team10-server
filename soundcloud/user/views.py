from django.contrib.auth import get_user_model, logout
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, permissions, viewsets
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from comment.models import Comment
from comment.serializers import UserCommentSerializer
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
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    followings=extend_schema(
        summary="Get User's Followings",
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    tracks=extend_schema(
        summary="Get User's Tracks",
        responses={
            200: OpenApiResponse(response=UserTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    likes_tracks=extend_schema(
        summary="Get User's Liked Tracks",
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    reposts_tracks=extend_schema(
        summary="Get User's Reposted Tracks",
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    comments=extend_schema(
        summary="Get User's Comments",
        responses={
            200: OpenApiResponse(response=UserCommentSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):

    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def get_serializer_class(self):
        if self.action in [ 'list', 'followers', 'followings' ]:
            return SimpleUserSerializer
        elif self.action in [ 'tracks' ]:
            return UserTrackSerializer
        elif self.action in [ 'likes_tracks', 'reposts_tracks' ]:
            return SimpleTrackSerializer
        elif self.action in [ 'comments' ]:
            return UserCommentSerializer
        else:
            return UserSerializer

    def get_queryset(self):
        if self.action in [ 'list', 'followers', 'followings' ]:
            return User.objects.prefetch_related('followers', 'owned_tracks')
        elif self.action in [ 'tracks' ]:
            return Track.objects.prefetch_related('likes', 'reposts', 'comments')
        elif self.action in [ 'likes_tracks', 'reposts_tracks' ]:
            return Track.objects.select_related('artist').prefetch_related('likes', 'reposts', 'comments', 'artist__followers', 'artist__owned_tracks')
        elif self.action in [ 'comments' ]:
            return Comment.objects.select_related('track').prefetch_related('track__likes', 'track__reposts', 'track__comments')
        else: 
            return User.objects.all()

    # Unlike GenericAPIView's get_object(self), this does not call self.get_queryset().
    # Always returns User object referred by {user_id}.
    def get_object(self):
        user_id = self.kwargs[self.lookup_url_kwarg]

        return get_object_or_404(User.objects.all(), id=user_id)

    @action(detail=True)
    def followers(self, *args, **kwargs):
        queryset = self.get_queryset().filter(followings__followee=self.get_object())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True)
    def followings(self, *args, **kwargs):
        queryset = self.get_queryset().filter(followers__follower=self.get_object())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True)
    def tracks(self, *args, **kwargs):
        queryset = self.get_queryset().filter(artist=self.get_object())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, url_path='likes/tracks')
    def likes_tracks(self, *args, **kwargs):
        queryset = self.get_queryset().filter(likes__user=self.get_object())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, url_path='reposts/tracks')
    def reposts_tracks(self, *args, **kwargs):
        queryset = self.get_queryset().filter(reposts__user=self.get_object())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True)
    def comments(self, *args, **kwargs):
        queryset = self.get_queryset().filter(writer=self.get_object())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


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

    queryset = User.objects.prefetch_related('followers', 'followings', 'owned_tracks', 'comments')
    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method in [ 'PUT', 'PATCH' ]:
            return UserMediaUploadSerializer
        else:
            return UserSerializer

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