from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from set.models import Set, SetTrack
from set.serializers import *
from soundcloud.utils import CustomObjectPermissions
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from user.models import User
from django.db import transaction

@extend_schema_view( #수정 필요
    create=extend_schema(
        summary="Create Set",
        parameters=[
            OpenApiParameter("track_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description='track id'),
        ],
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
    track=extend_schema(
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
    
    # 1. POST /sets/ 한 곡으로 playlist 생성 시
    @transaction.atomic
    def create(self, request):
        try:
            track_id = request.data["track_id"]
        except:
            return Response({"error": "track_id is required data."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            return Response({"error": "해당 트랙은 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set = serializer.save()
        SetTrack.objects.create(set=set, track=track)
        set.image = track.image
        set.save()
        return Response(self.get_serializer(set).data, status=status.HTTP_201_CREATED)


    # 2. PUT /sets/{set_id} - PATCH 는 상속 그대로
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        set = self.get_object()
        serializer = self.get_serializer(set, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.update(set, serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 3. GET /sets/{set_id}
    def retrieve(self, request, *args, **kwargs):
        set = self.get_object()
        return Response(self.get_serializer(set).data, status=status.HTTP_200_OK)

    # 4. DELETE /sets/{set_id}
    def destroy(self, request, *args, **kwargs):
        set = self.get_object()
        set.set_tracks.all().delete() #관계도 지우기. 트랙은 남아있음
        set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    # 5. POST /sets/{set_id}/track/ (add track to playlist)
    # 6. DELETE /sets/{set_id}/track/ (remove track from playlist)
    @action(methods=['POST', 'DELETE'], detail=True)
    def tracks(self, request, *args, **kwargs):
        user = self.request.user #CustomObjectPerm 이 커버가능한지 확인하기 - x
        #set = self.get_object()
        try:
            set = Set.objects.get(id=self.kwargs[self.lookup_url_kwarg])
        except Set.DoesNotExist:
            return Response({"error": "해당 셋은 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        if user != set.creator:
            return Response({"error": "해당 셋의 creator가 아닙니다."}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        track_id = data["track_id"]
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            return Response({"error": "해당 트랙은 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'POST':
            return self._add(set, track)
        else:
            return self._remove(set, track)

    def _add(self, set, track):
        if set.set_tracks.filter(track=track).exists():
            return Response({"error": "이미 셋에 추가되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        SetTrack.objects.create(set=set, track=track)
        if set.image is None:
            set.image = track.image
            set.save()
        return Response({"added to playlist."}, status=status.HTTP_200_OK) 

    def _remove(self, set, track):
        try:
            set_track = set.set_tracks.get(track=track)
        except SetTrack.DoesNotExist: 
            return Response({"error": "셋에 추가된 트랙이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        set_track.delete()

        if set.set_tracks.count() == 0:
            set.image = None
            set.save()
        return Response({"removed from playlist"}, status=status.HTTP_200_OK)

    # 7. GET /sets/{set_id}/likers
    @action(detail=True)
    def likers(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # 8. GET /sets/{set_id}/reposters
    @action(detail=True)
    def reposters(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

