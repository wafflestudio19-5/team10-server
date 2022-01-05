from rest_framework import status, viewsets
from rest_framework.response import Response
from set.models import Set, SetTrack
from set.serializers import *
from soundcloud.utils import CustomObjectPermissions
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

class SetViewSet(viewsets.GenericViewSet):
    query_set = Set.objects.all()
    permission_classes = (CustomObjectPermissions, )

    #serializer_class = SetSerializer
    def get_sealizer_class(self):
        if self.action in ['create', 'update']:
            return SetUploadSerializer
        else:
            return SetSerializer
    
    # 1. POST /sets/
    @extend_schema_view( #수정 필요
        create=extend_schema(
            summary="Signup",
            responses={
                201: OpenApiResponse(response=SetUploadSerializer, description='Created'),
                400: OpenApiResponse(description='Bad Request'),
                401: OpenApiResponse(description='Unauthorized'),
            }
        )
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        if set.creator != request.user:
            return Response({"error": "set of others"}, status=403)
        SetTrack.objects.filter(set=set).delete() #트랙은 남아있음
        set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


