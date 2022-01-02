from django.db import models
from django.contrib.auth import get_user_model
from track.models import Track

# Create your models here.
class Comment(models.Model):
    writer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    commented_at = models.TimeField(auto_now_add=True)
    parent_comment = models.OneToOneField('self', null=True, related_name="reply", on_delete=models.SET_NULL) ##linkedlist
