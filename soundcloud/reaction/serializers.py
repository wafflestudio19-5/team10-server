from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from track.models import Track
from set.models import Set
from reaction.models import Like, Repost
from soundcloud.exceptions import ConflictError
from rest_framework import status

class LikeService(serializers.Serializer):

    def execute(self):
        type = self.context.get('type')
        id = self.context.get('id')
        method = self.context.get('method')
        user = self.context.get('user')

        if type == 'track':
            track = get_object_or_404(Track, permalink=id)
            if method == 'POST':
                try:
                    Like.objects.get(track__id=track.id, user=user)
                    raise ConflictError("Already liked")
                except Like.DoesNotExist:
                    Like.objects.create(content_object=track, user=user)
                    return status.HTTP_201_CREATED, 'Liked'
            elif method == 'DELETE':
                like = get_object_or_404(Like, track__id=track.id, user=user)
                like.delete()

                return status.HTTP_200_OK, 'Unliked'
        elif type == 'set':
            set = get_object_or_404(Set, permalink=id)
            if method == 'POST':
                try:
                    Like.objects.get(set__id=set.id, user=user)
                    raise ConflictError("Already liked")
                except Like.DoesNotExist:
                    Like.objects.create(content_object=set, user=user)
                    return status.HTTP_201_CREATED, 'Liked'
            elif method == 'DELETE':
                like = get_object_or_404(Like, set__id=set.id, user=user)
                like.delete()

                return status.HTTP_200_OK, 'Unliked'


class RepostService(serializers.Serializer):

    def execute(self):
        type = self.context.get('type')
        id = self.context.get('id')
        method = self.context.get('method')
        user = self.context.get('user')

        if type == 'track':
            track = get_object_or_404(Track, permalink=id)
            if method == 'POST':
                try:
                    Repost.objects.get(track__id=track.id, user=user)
                    raise ConflictError("Already reposted")
                except Repost.DoesNotExist:
                    Repost.objects.create(content_object=track, user=user)
                    return status.HTTP_201_CREATED, 'Reposted'
            elif method == 'DELETE':
                repost = get_object_or_404(Repost, track__id=track.id, user=user)
                repost.delete()

                return status.HTTP_200_OK, 'Unreposted'
        elif type == 'set':
            set = get_object_or_404(Set, permalink=id)
            if method == 'POST':
                try:
                    Repost.objects.get(set__id=set.id, user=user)
                    raise ConflictError("Already reposted")
                except Repost.DoesNotExist:
                    Repost.objects.create(content_object=set, user=user)
                    return status.HTTP_201_CREATED, 'Reposted'
            elif method == 'DELETE':
                repost = get_object_or_404(Repost, set__id=set.id, user=user)
                repost.delete()

                return status.HTTP_200_OK, 'Unreposted'