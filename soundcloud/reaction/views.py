from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from track.models import Track
from set.models import Set
from .models import Like, Repost


class LikeTrackAPIView(GenericAPIView):

    queryset = Like.objects
    serializer_class = serializers.Serializer
    lookup_field = 'track_id'

    def post(self, request, track_id=None):
        track = get_object_or_404(Track, id=track_id)

        try:
            self.get_queryset().get(track__id=track.id, user=request.user)
            raise ValidationError("Already liked")
        except ObjectDoesNotExist:
            self.get_queryset().create(content_object=track, user=request.user)
            return Response(data='Liked', status=status.HTTP_200_OK)

    def delete(self, request, track_id=None):
        track = get_object_or_404(Track, id=track_id)

        try:
            like = self.get_queryset().get(track__id=track.id, user=request.user)
            like.delete()
            return Response(data='Unliked', status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            raise ValidationError("Not liked")


class LikeSetAPIView(GenericAPIView):

    queryset = Like.objects
    serializer_class = serializers.Serializer
    lookup_field = 'set_id'

    def post(self, request, set_id=None):
        set = get_object_or_404(Set, id=set_id)

        try:
            self.get_queryset().get(set__id=set.id, user=request.user)
            raise ValidationError("Already Liked")
        except ObjectDoesNotExist:
            self.get_queryset().create(content_object=set, user=request.user)
            return Response(data='Liked', status=status.HTTP_200_OK)

    def delete(self, request, set_id=None):
        set = get_object_or_404(Set, id=set_id)

        try:
            like = self.get_queryset().get(set__id=set.id, user=request.user)
            like.delete()
            return Response(data='Unliked', status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            raise ValidationError("Not liked")
