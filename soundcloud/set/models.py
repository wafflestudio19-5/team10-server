from django.db import models
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from track.models import Track
from reaction.models import Like, Repost
from tag.models import Tag 
from soundcloud.utils import assign_object_perms

class CustomSetManager(models.Manager):

    def create(self, **kwargs):
        instance = super().create(**kwargs)
        assign_object_perms(instance.creator, instance)

        return instance

    def get_queryset(self):

        return super().get_queryset().annotate(
            track_count=Count('tracks', distinct=True),
            like_count=Count('likes', distinct=True),
            repost_count=Count('reposts', distinct=True),
        ).prefetch_related('creator__followers', 'creator__owned_tracks').select_related('creator')


class Set(models.Model):
    PLAYLIST = 'playlist'
    ALBUM = 'album'
    EP = 'ep'
    SINGLE = 'single'
    COMPILATION = 'compilation'
    STATION = 'station'
    SET_TYPE_CHOICES=[
        (PLAYLIST, PLAYLIST),
        (ALBUM, ALBUM),
        (EP, EP),
        (SINGLE, SINGLE),
        (COMPILATION, COMPILATION),
        (STATION, STATION),
    ]

    SET_TYPES = (PLAYLIST, ALBUM, EP, SINGLE, COMPILATION, STATION)
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(get_user_model(), related_name="owned_sets", on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=SET_TYPE_CHOICES, db_index=True) ## choices
    permalink = models.SlugField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    genre = models.ForeignKey(Tag, related_name="genre_sets", null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, related_name="tag_sets")
    is_private = models.BooleanField(default=False)
    likes = GenericRelation(Like, related_query_name="set") 
    reposts = GenericRelation(Repost, related_query_name="set") 
    players = models.ManyToManyField(get_user_model(), related_name="played_sets", through='SetHit')
    image = models.URLField(null=True, unique=True)
    tracks = models.ManyToManyField(Track, through='SetTrack', related_name='sets')

    objects = CustomSetManager()

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=['creator', 'permalink'],
                name='set_permalink_unique',
            ),
        ]

class SetTrack(models.Model):
    set = models.ForeignKey(Set, related_name='set_tracks', on_delete=models.CASCADE)
    track = models.ForeignKey(Track, related_name='set_tracks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class SetHit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    last_hit = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-last_hit', )
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'set'],
                name='set_hit_unique',
            ),
        ]
