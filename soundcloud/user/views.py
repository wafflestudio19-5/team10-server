from django.contrib.auth import get_user_model, logout
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from user.serializers import UserLoginSerializer, UserCreateSerializer

User = get_user_model()


class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response("이미 존재하는 이메일입니다.", status=status.HTTP_409_CONFLICT)

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        return Response({'profile_id': user.profile_id, 'token': token}, status=status.HTTP_201_CREATED)


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
