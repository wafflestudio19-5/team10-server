from django.db import models, transaction
from django.contrib.auth import get_user_model
from soundcloud.utils import assign_object_perms
from track.models import Track


class CustomCommentManager(models.Manager):

    @transaction.atomic
    def create(self, **kwargs):
        kwargs['group'] = kwargs.get('group') or Group.objects.create(track=kwargs.get('track'))
        instance = super().create(**kwargs)
        assign_object_perms(instance.writer, instance)

        return instance


class Group(models.Model):

    track = models.ForeignKey(Track, related_name='comment_groups', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):

    group = models.ForeignKey(Group, related_name='comments', on_delete=models.CASCADE)
    writer = models.ForeignKey(get_user_model(), related_name='comments', on_delete=models.CASCADE)
    track = models.ForeignKey(Track, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    commented_at = models.TimeField(auto_now_add=True)

    objects = CustomCommentManager()
