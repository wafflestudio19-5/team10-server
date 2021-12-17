from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from track.models import Track
from reaction.models import Like, Repost
from tag.models import Tag 


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
    permalink = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="sets")
    tracks = models.ManyToManyField(Track, related_name="sets") ##null has no effect on MTM field
    is_private = models.BooleanField(default=False)
    likes = GenericRelation(Like, related_query_name="set") ##추가
    reposts = GenericRelation(Repost, related_query_name="set") ##추가
    #image = models.ImageField(null=True, blank=True, upload_to=?)