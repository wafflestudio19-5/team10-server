from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import re
from urllib.parse import urlparse
from track.models import Track
from set.models import Set

User = get_user_model()


class ResolveSerializer(serializers.Serializer):
    link = serializers.CharField()


class ResolveService(serializers.Serializer):

    def execute(self):
        url = self.context['request'].GET.get('url')
        url_parsed = urlparse(url)

        if url_parsed.hostname not in [ 'www.soundwaffle.com', 'soundwaffle.com' ]:
            raise ValidationError("잘못된 hostname입니다.")

        url_path = url_parsed.path

        pattern_user = re.compile('^/[a-z0-9_-]{3,25}$')
        pattern_track = re.compile('^/[a-z0-9_-]{3,25}/[a-z0-9_-]{3,255}$')
        pattern_set = re.compile('^/[a-z0-9_-]{3,25}/sets/[a-z0-9_-]{3,255}$')

        if pattern_user.match(url_path):    # user
            user_permalink = url_path.split('/')[1]
            user = get_object_or_404(User, permalink=user_permalink)
            api_url = "https://api.soundwaffle.com/users/" + str(user.id)
            return status.HTTP_200_OK, api_url
        elif pattern_track.match(url_path):  # track
            user_permalink = url_path.split('/')[1]
            track_permalink = url_path.split('/')[2]
            user = get_object_or_404(User, permalink=user_permalink)
            track = get_object_or_404(Track, artist=user, permalink=track_permalink)
            api_url = "https://api.soundwaffle.com/tracks/" + str(track.id)
            return status.HTTP_200_OK, api_url
        elif pattern_set.match(url_path):  # set
            user_permalink = url_path.split('/')[1]
            set_permalink = url_path.split('/')[3]
            user = get_object_or_404(User, permalink=user_permalink)
            set = get_object_or_404(Set, creator=user, permalink=set_permalink)
            api_url = "https://api.soundwaffle.com/sets/" + str(set.id)
            return status.HTTP_200_OK, api_url
        else:
            raise ValidationError("잘못된 URL 경로입니다.")
