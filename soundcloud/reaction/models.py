from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

reaction_limit = models.Q(app_label='track', model='Track') | models.Q(app_label='set', model='Set')

class Like(models.Model):

    user = models.ForeignKey(get_user_model(), related_name="likes", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, limit_choices_to=reaction_limit, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='like_unique'
            ),
        ]


class Repost(models.Model):

    user = models.ForeignKey(get_user_model(), related_name="reposts", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, limit_choices_to=reaction_limit, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='repost_unique',
            ),
        ]
