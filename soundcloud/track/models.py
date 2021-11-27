from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from reaction.models import Like, Repost
from tag.models import Tag

class Track(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(get_user_model(), related_name="owned_tracks", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    #image = models.ImageField(null=True, blank=True, upload_to=?)
    count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name="tracks")
    is_private = models.BooleanField(default=False)
    likes = GenericRelation(Like, related_query_name="track") ##추가
    reposts = GenericRelation(Repost, related_query_name="track") ##추가