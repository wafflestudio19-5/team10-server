from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, extend_schema
from utility.serializers import ResolveSerializer, ResolveService

User = get_user_model()


class ResolveView(APIView):

    @extend_schema(
        summary="Resolves soundwaffle.com URLs to Resource URLs to use with the API.",
        parameters=[
            OpenApiParameter(
                name="url",
                type=str,
                location=OpenApiParameter.QUERY,
                description="SoundWaffle URL",
                required=True,
            )
        ],
        responses={
            200: OpenApiResponse(response=ResolveSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
            404: OpenApiResponse(description='Not Found'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        User  : https%3A%2F%2Fsoundwaffle.com%2F{user_permalink} \n
        Track : https%3A%2F%2Fsoundwaffle.com%2F{user_permalink}%2F{track_permalink} \n
        Set   : https%3A%2F%2Fsoundwaffle.com%2F{user_permalink}%2Fsets%2F{set_permalink} \n
        위의 세 가지 permalink 기반의 URL로부터 각 object의 정보를 불러올 수 있는 id 기반의 API 서버 URL을 반환함
        """

        service = ResolveService(context={'request': request})
        status_code, link = service.execute()
        return Response(status=status_code, data=ResolveSerializer({'link': link}).data)
