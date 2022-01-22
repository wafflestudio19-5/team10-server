from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from reaction.models import Like, Repost
from soundcloud.utils import assign_object_perms
from tag.models import Tag


class CustomTrackManager(models.Manager):

    def create(self, **kwargs):
        instance = super().create(**kwargs)
        assign_object_perms(instance.artist, instance)

        return instance

    def get_queryset(self):

        return super().get_queryset().select_related('artist', 'genre').prefetch_related('hits', 'likes', 'reposts', 'comments', 'tags')


class Track(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(get_user_model(), related_name="owned_tracks", on_delete=models.CASCADE)
    permalink = models.SlugField(max_length=255)
    audio = models.URLField(unique=True)
    image = models.URLField(null=True, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    genre = models.ForeignKey(Tag, related_name="genre_tracks", null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, related_name="tag_tracks")
    is_private = models.BooleanField(default=False)
    likes = GenericRelation(Like, related_query_name="track")
    reposts = GenericRelation(Repost, related_query_name="track")

    objects = CustomTrackManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['artist', 'permalink'],
                name='track_permalink_unique',
            ),
        ]

class TrackHit(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='play_history', on_delete=models.CASCADE, null=True)
    track = models.ForeignKey(Track, related_name='hits', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )