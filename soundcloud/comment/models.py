from django.db import models
from django.contrib.auth import get_user_model
from soundcloud.utils import assign_object_perms
from track.models import Track


class CustomCommentManager(models.Manager):

    def create(self, **kwargs):
        instance = super().create(**kwargs)
        assign_object_perms(instance.writer, instance)

        return instance


class Comment(models.Model):
    writer = models.ForeignKey(get_user_model(), related_name='comments', on_delete=models.CASCADE)
    track = models.ForeignKey(Track, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    commented_at = models.TimeField(auto_now_add=True)
    parent_comment = models.OneToOneField('self', null=True, related_name="reply", on_delete=models.SET_NULL) ##linkedlist

    objects = CustomCommentManager()
