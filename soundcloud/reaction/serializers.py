from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from reaction.models import Like, Repost
from soundcloud.utils import ConflictError


class BaseReactionService(serializers.Serializer):

    reaction_type = None

    def create(self):
        user = self.context.get('request').user
        target = self.context.get('target')
        content_type = ContentType.objects.get_for_model(target)

        if self.reaction_type.objects.filter(user=user, object_id=target.id, content_type=content_type).exists():
            raise ConflictError(f"User <{user}>'s reaction <{self.reaction_type.__name__}> to <{target}> already exists.")
        self.reaction_type.objects.create(user=user, content_object=target)

        return status.HTTP_201_CREATED, f"Reaction <{self.reaction_type.__name__}> created."

    def delete(self):
        user = self.context.get('request').user
        target = self.context.get('target')
        content_type = ContentType.objects.get_for_model(target)

        try:
            self.reaction_type.objects.get(user=user, object_id=target.id, content_type=content_type).delete()
        except self.reaction_type.DoesNotExist:
            raise NotFound(f"User <{user}>'s reaction <{self.reaction_type.__name__}> to <{target}> does not exist.")

        return status.HTTP_200_OK, f"Reaction <{self.reaction_type.__name__}> deleted."


class LikeService(BaseReactionService):

    reaction_type = Like


class RepostService(BaseReactionService):

    reaction_type = Repost
