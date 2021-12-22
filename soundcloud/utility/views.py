from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from track.models import Track
from set.models import Set

User = get_user_model()


class ResolveView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        """
        User  : https%3A%2F%2Fsoundcloud.com%2F{user_permalink}
        Track : https%3A%2F%2Fsoundcloud.com%2F{user_permalink}%2F{track_permalink}
        Set   : https%3A%2F%2Fsoundcloud.com%2F{user_permalink}%2Fsets%2F{set_permalink}
        위의 세 가지 permalink 기반의 URL로부터 각 object의 정보를 불러올 수 있는 id 기반의 API 서버 URL을 반환함
        """

        if not request.user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")

        url = request.GET.get('url')  # /resolve?url={url}
        url_split = url.split('/')

        if len(url_split) == 4:    # user
            permalink = url_split[3]
            user = get_object_or_404(User, permalink=permalink)
            api_url = "https://api.soundwafle.com/users/" + str(getattr(user, 'id'))
            return Response(status=status.HTTP_302_FOUND, data={"link": api_url})
        elif len(url_split) == 5:  # track
            permalink = url_split[4]
            track = get_object_or_404(Track, permalink=permalink)
            api_url = "https://api.soundwafle.com/tracks/" + str(getattr(track, 'id'))
            return Response(status=status.HTTP_302_FOUND, data={"link": api_url})
        elif len(url_split) == 6:  # set
            permalink = url_split[5]
            set = get_object_or_404(Set, permalink=permalink)
            api_url = "https://api.soundwafle.com/sets/" + str(getattr(set, 'id'))
            return Response(status=status.HTTP_302_FOUND, data={"link": api_url})
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data="잘못된 URL이 입력되었습니다.")
