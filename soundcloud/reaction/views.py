from rest_framework import status, permissions, views
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from track.models import Track
from set.models import Set
from .models import Like, Repost


class LikeTrackAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, pk=None):
        track = get_object_or_404(Track, permalink=pk)
        ct = ContentType.objects.get_for_model(track)
        try:
            Like.objects.get(content_type=ct, object_id=track.id, user=request.user)
            return Response(data='Already like', status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            Like.objects.create(content_object=track, user=request.user)
            return Response(data='like', status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        track = get_object_or_404(Track, permalink=pk)
        ct = ContentType.objects.get_for_model(track)
        try:
            like = Like.objects.get(content_type=ct, object_id=track.id, user=request.user)
            like.delete()
            return Response(data='unlike', status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(data='Already unlike', status=status.HTTP_400_BAD_REQUEST)


class LikeSetAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk=None):
        set = get_object_or_404(Set, permalink=pk)
        ct = ContentType.objects.get_for_model(set)
        try:
            Like.objects.get(content_type=ct, object_id=set.id, user=request.user)
            return Response(data='Already like', status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            Like.objects.create(content_object=set, user=request.user)
            return Response(data='like', status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        set = get_object_or_404(Set, permalink=pk)
        ct = ContentType.objects.get_for_model(set)
        try:
            like = Like.objects.get(content_type=ct, object_id=set.id, user=request.user)
            like.delete()
            return Response(data='unlike', status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(data='Already unlike', status=status.HTTP_400_BAD_REQUEST)
