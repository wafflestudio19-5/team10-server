from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

class Like(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="likes", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

class Repost(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="reposts", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

class Tag(models.Model):
    name = models.CharField(max_length=20)

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
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="sets")
    tracks = models.ManyToManyField(Track, related_name="sets") ##null has no effect on MTM field
    is_private = models.BooleanField(default=False)
    likes = GenericRelation(Like, related_query_name="set") ##추가
    reposts = GenericRelation(Repost, related_query_name="set") ##추가
    #image = models.ImageField(null=True, blank=True, upload_to=?)

class Comment(models.Model):
    writer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    commented_at = models.TimeField(default="00:00")
    parent_comment = models.ForeignKey('self', null=True, related_name="reply", on_delete=models.CASCADE) ##oneToOne?

    