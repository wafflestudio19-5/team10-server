from django.contrib.auth import get_user_model, logout
from rest_framework import status, permissions, viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response
from user.serializers import UserLoginSerializer, UserCreateSerializer, UserSerializer

User = get_user_model()


class UserSignUpView(GenericAPIView):

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
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

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserLogoutView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        logout(request)

        return Response({"you\'ve been logged out"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.GenericViewSet):

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, pk=None):

        if pk == 'me' and not request.user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        user = request.user if pk == 'me' else get_object_or_404(
            User, id=pk)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
