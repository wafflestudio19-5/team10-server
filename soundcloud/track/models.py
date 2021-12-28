from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from reaction.models import Like, Repost
from tag.models import Tag


class Track(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(get_user_model(), related_name="owned_tracks", on_delete=models.CASCADE)
    permalink = models.CharField(max_length=255)
    audio = models.URLField(unique=True)
    image = models.URLField(null=True, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(default=0)
    genre = models.ForeignKey(Tag, related_name="genre_tracks", null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, related_name="tag_tracks")
    is_private = models.BooleanField(default=False)
    likes = GenericRelation(Like, related_query_name="track")
    reposts = GenericRelation(Repost, related_query_name="track")

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=['artist', 'permalink'],
                name='track_permalink_unique',
            ),
        ]
