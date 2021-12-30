from rest_framework import status, viewsets
from rest_framework.response import Response
from set.models import Set, SetTrack
from set.serializers import *

class SetViewSet(viewsets.GenericViewSet):
    query_set = Set.objects.all()
    #serializer_class = SetSerializer
    def get_sealizer_class(self):
        if self.action in ['create', 'update']:
            return TrackUploadSerializer
        else:
            return SetSerializer
    
    # 1. POST /sets/
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # 2. PUT /sets/{set_id}
    def update(self, request, pk):

        return

    # 3. GET /sets/{set_id}
    def retrieve(self, request, pk):

        return

    # 4. DELETE /sets/{set_id}
    def delete(self, request, pk):

        return


