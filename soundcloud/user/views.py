from django.contrib.auth import get_user_model, logout
from rest_framework import status, permissions, viewsets
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from user.serializers import *
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

User = get_user_model()


class UserSignUpView(GenericAPIView):

    serializer_class = UserCreateSerializer
    queryset = User.objects.select_related('email')
    permission_classes = (permissions.AllowAny, )

    @extend_schema(
        summary="Signup",
        tags=['auth', ],
        responses={
            201: OpenApiResponse(response=UserCreateSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
    def post(self, request, *args, **kwargs):

        # Should check whether the email already exists in DB before validation.
        email = request.data.get('email')
        if self.get_queryset().filter(email=email).exists():
            return Response("이미 존재하는 이메일입니다.", status=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data, status=status.HTTP_201_CREATED)


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
        data = serializer.execute()

        return Response(data, status=status.HTTP_200_OK)


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
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    followings=extend_schema(
        summary="Get User's Followees",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserSerializer
        elif self.action == 'list':
            return SimpleUserSerializer
  
    @extend_schema(
        methods=['POST'],
        summary="Follow User",
        responses={
            201: OpenApiResponse(response=UserSerializer, description='Created'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
    @extend_schema(
        methods=['DELETE'],
        summary="Unfollow User",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=(permissions.IsAuthenticated,))
    def follow(self, request, user_id=None):
        if request.method == 'POST':
            service = UserFollowService(context={'request': request, 'user_id': user_id})
            status_code, data = service.execute()
            return Response(status=status_code, data=data)

        if request.method == 'DELETE':
            service = UserUnfollowService(context={'request': request, 'user_id': user_id})
            status_code, data = service.execute()
            return Response(status=status_code, data=data)

    @action(detail=True)
    def followers(self, request, user_id=None):
        service = FollowerRetrieveService(context={'user_id': user_id})
        status_code, data = service.execute()
        return Response(status=status_code, data=data)

    @action(detail=True)
    def followings(self, request, user_id=None):
        service = FolloweeRetrieveService(context={'request': request, 'user_id': user_id})
        status_code, data = service.execute()
        return Response(status=status_code, data=data)


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
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    patch=extend_schema(
        summary="Partial Update Me",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
)
class UserSelfView(RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    queryset = None
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        return self.request.user
