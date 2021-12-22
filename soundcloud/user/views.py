from django.contrib.auth import get_user_model, logout
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response
from user.serializers import UserLoginSerializer, UserCreateSerializer, UserSerializer, UserTokenSerializer
from drf_spectacular.utils import OpenApiResponse, extend_schema

User = get_user_model()


class UserSignUpView(GenericAPIView):

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserCreateSerializer

    @extend_schema(
        summary="Signup", tags=['auth'],
        request={
            'application/json': serializer_class,
            'application/x-www-form-urlencoded': serializer_class,
        },
        responses={
            201: OpenApiResponse(response=UserTokenSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            409: OpenApiResponse(description='Conflict'),
        }
    )
    def post(self, request, *args, **kwargs):

        # Should check whether the email already exists in DB before validation.
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response("이미 존재하는 이메일입니다.", status=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginView(GenericAPIView):

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="Login", tags=['auth'],
        request={
            'application/json': serializer_class,
            'application/x-www-form-urlencoded': serializer_class,
        },
        responses={
            200: OpenApiResponse(response=UserTokenSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserLogoutView(GenericAPIView):

    @extend_schema(
        summary="Logout", tags=['auth'],
        description="Do nothing, actually.",
        responses={
            200: OpenApiResponse(description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    )
    def post(self, request):
        logout(request)

        return Response({"you\'ve been logged out"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.GenericViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'user_id'

    @extend_schema(
        summary="Retrieve User",
        description="Typically {user_id} is an integer.\n\nIt may be specified as {user_id} = 'me' only if the proper authorization credentials are provided.",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def retrieve(self, request, user_id=None):

        if user_id == 'me' and not request.user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        user = request.user if user_id == 'me' else get_object_or_404(User, id=user_id)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
