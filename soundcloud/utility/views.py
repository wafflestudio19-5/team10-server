from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from utility.schemas import *
from utility.serializers import ResolveService

User = get_user_model()


@resolve_schema
class ResolveView(APIView):

    def get(self, request, *args, **kwargs):
        """
        User  : https%3A%2F%2Fsoundwaffle.com%2F{user_permalink} \n
        Track : https%3A%2F%2Fsoundwaffle.com%2F{user_permalink}%2F{track_permalink} \n
        Set   : https%3A%2F%2Fsoundwaffle.com%2F{user_permalink}%2Fsets%2F{set_permalink} \n
        위의 세 가지 permalink 기반의 URL로부터 각 object의 정보를 불러올 수 있는 id 기반의 API 서버 URL을 반환함
        """

        service = ResolveService(context={'request': request})
        url = service.execute()
        return Response(status=status.HTTP_302_FOUND, headers={'Location': url})
