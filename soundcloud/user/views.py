from django.contrib.auth import get_user_model, logout
from django.db import IntegrityError
from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from user.serializers import UserLoginSerializer, UserCreateSerializer, UserSerializer

User = get_user_model()

class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT, data='이미 존재하는 유저입니다.')

        return Response({'profile_id': user.profile_id, 'token': jwt_token}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny, )

    def put(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        logout(request)
        return Response({'success': True}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.GenericViewSet):

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, pk=None):

        if pk == 'me':
            if request.user.is_authenticated:
                return Response(self.get_serializer(request.user).data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN, data='먼저 로그인 하세요.')
        else:
            user = User.objects.get(profile_id=pk)
            if user is None:
                return Response(status=status.HTTP_404_NOT_FOUND, data='해당 유저는 존재하지 않습니다.')
            else:
                return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
