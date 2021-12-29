from django.contrib.auth import get_user_model, logout
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from user.serializers import UserLoginSerializer, UserCreateSerializer, UserSerializer, \
    UserFollowService, UserUnfollowService, FollowerRetrieveService, FolloweeRetrieveService
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

User = get_user_model()


class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response("이미 존재하는 이메일입니다.", status=status.HTTP_409_CONFLICT)

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny, )

    def put(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        logout(request)
        
        return Response({"you\'ve been logged out"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.GenericViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def retrieve(self, request, user_id=None):

        if user_id == 'me' and not request.user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        user = request.user if user_id == 'me' else get_object_or_404(User, id=user_id)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

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
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=(permissions.IsAuthenticated, ))
    def follow(self, request, user_id=None):
        
        if request.method == 'POST':
            service = UserFollowService(context={'request': request, 'user_id': user_id})
            status_code, data = service.execute()
            return Response(status=status_code, data=data)

        if request.method == 'DELETE':
            service = UserUnfollowService(context={'request': request, 'user_id': user_id})
            status_code, data = service.execute()
            return Response(status=status_code, data=data)

    @extend_schema(
        summary="Get User's Followers",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    @action(detail=True, methods=['GET'])
    def followers(self, request, user_id=None):
        service = FollowerRetrieveService(context={'user_id': user_id})
        status_code, data = service.execute()
        return Response(status=status.HTTP_200_OK, data=data)

    @extend_schema(
        summary="Get User's Followees",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    @action(detail=True, methods=['GET'])
    def followings(self, request, user_id=None):
        service = FolloweeRetrieveService(context={'request': request, 'user_id': user_id})
        status_code, data = service.execute()
        return Response(status=status.HTTP_200_OK, data=data)
