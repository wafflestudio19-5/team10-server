from rest_framework import status, viewsets
from rest_framework.response import Response
from set.models import Set, SetTrack
from set.serializers import *
from soundcloud.utils import CustomObjectPermissions
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

@extend_schema_view( #수정 필요
    create=extend_schema(
        summary="Create Set",
        responses={
            201: OpenApiResponse(response=SetSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve Set",
        responses={
            '200': OpenApiResponse(response=SetSerializer, description='OK'),
            '404': OpenApiResponse(description='Not Found')
        }
    ),
    destroy=extend_schema(
        summary="Delete Set",
        responses={
            '204': OpenApiResponse(description='No Content'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    )
)
class SetViewSet(viewsets.GenericViewSet):
    queryset = Set.objects.all()
    permission_classes = (CustomObjectPermissions, )

    #serializer_class = SetSerializer
    def get_serializer_class(self):
        if self.action in ['update']:
            return SetUploadSerializer
        else:
            return SetSerializer
    
    # 1. POST /sets/ 한 곡으로 playlist 생성 시
    def create(self, request):
        track_id = request.data["track_id"]
        track = Track.objects.get(id=track_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set = serializer.save()
        SetTrack.objects.create(set=set, track=track)
        set.image = track.image
        set.save()
        return Response(self.get_serializer(set).data, status=status.HTTP_201_CREATED)


    # 2. PUT /sets/{set_id}
    def update(self, request, pk):
        set = self.get_object()
        serializer = self.get_serializer(set, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(set, serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 3. GET /sets/{set_id}
    def retrieve(self, request, pk):
        set = self.get_object()
        return Response(self.get_serializer(set).data, status=status.HTTP_200_OK)

    # 4. DELETE /sets/{set_id}
    def destroy(self, request, pk):
        set = self.get_object()
        SetTrack.objects.filter(set=set).delete() #관계도 지우기. 트랙은 남아있음
        set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


