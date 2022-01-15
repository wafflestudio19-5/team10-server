from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from set.models import Set, SetTrack
from set.serializers import *
from soundcloud.utils import CustomObjectPermissions
from track.models import Track
from user.models import User


@extend_schema_view( 
    create=extend_schema(
        summary="Create Set",
        responses={
            201: OpenApiResponse(response=SetSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    update=extend_schema(
        summary="Update Set",
        responses={
            '200': OpenApiResponse(response=SetMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    partial_update=extend_schema(
        summary="Partial Update Set",
        responses={
            '200': OpenApiResponse(response=SetMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
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
    ),
    tracks=extend_schema(
        summary="Add/Remove Track in Set",
        # parameters=[
        #     OpenApiParameter("track_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description='track id'),
        # ],
        responses={
            '200': OpenApiResponse(description='OK'),
            '400': OpenApiResponse(description="Bad Request"),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    likers=extend_schema(
        summary="Get Set's Likers",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    reposters=extend_schema(
        summary="Get Set's Reposters",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    )

)
class SetViewSet(viewsets.ModelViewSet):
    permission_classes = (CustomObjectPermissions, )
    filter_backends = (OrderingFilter, )
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_url_kwarg = 'set_id'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return SetMediaUploadSerializer
        if self.action in ['likers', 'reposters']:
            return SimpleUserSerializer
        if self.action in ['tracks']:
            return SetTrackService
        else:
            return SetSerializer

    def get_queryset(self):
        if self.action in ['likers', 'reposters']:
            self.set = getattr(self, 'set', None) or get_object_or_404(Set, id=self.kwargs[self.lookup_url_kwarg])
            if self.action == 'likers':
                return User.objects.prefetch_related('followers', 'owned_sets').filter(likes__set=self.set)
            if self.action == 'reposters':
                return User.objects.prefetch_related('followers', 'owned_sets').filter(reposts__set=self.set)
        else:
            return Set.objects.all()
    
    # 1. POST /sets/ - 빈 playlist 생성 - mixin 이용
    # 2. PUT /sets/{set_id} - mixin 이용
    # 3. GET /sets/{set_id} - mixin 이용
    # 4. DELETE /sets/{set_id} - mixin 이용
    # 7. GET /sets/{set_id}/likers
    @action(detail=True)
    def likers(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # 8. GET /sets/{set_id}/reposters
    @action(detail=True)
    def reposters(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class SetTrackViewSet(viewsets.GenericViewSet):
    permission_classes = (CustomObjectPermissions, )
    lookup_url_kwarg = 'set_id'
    serializer_class = SetTrackService
    

    # 5. POST /sets/{set_id}/track/ (add track to playlist)
    # 6. DELETE /sets/{set_id}/track/ (remove track from playlist)
    @action(methods=['POST', 'DELETE'], detail=True)
    def tracks(self, request, *args, **kwargs):
        user = self.request.user 
        set = self.get_object()
        service = self.get_serializer()

        # data = request.data
        # track_id = data["track_id"] #track_id 필수.
        # try:
        #     track = Track.objects.get(id=track_id)
        # except Track.DoesNotExist:
        #     return Response({"error": "해당 트랙은 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'POST':
            return self._add(service)
        else:
            return self._remove(service)


    def _add(self, service):
        status, data = service.create()

        # if set.set_tracks.filter(track=track).exists():
        #     return Response({"error": "이미 셋에 추가되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # set.tracks.add(track)
        # set.save()
        return Response(status=status, data=data)
        #return Response({"added to playlist."}, status=status.HTTP_200_OK) 

    def _remove(self, service):
        #set.tracks.remove(track)
        status, data = service.delete()
        return Response(status=status, data=data)
        #return Response({"removed from playlist"}, status=status.HTTP_200_OK)



