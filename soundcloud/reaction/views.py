from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import serializers
from serializers import LikeService, RepostService


class LikeTrackAPIView(GenericAPIView):

    serializer_class = serializers.Serializer
    lookup_field = 'track_id'

    def post(self, request, track_id=None):
        service = LikeService(context={'user': request.user, 'type': 'track', 'method': 'POST', 'id': track_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)

    def delete(self, request, track_id=None):
        service = LikeService(context={'user': request.user, 'type': 'track', 'method': 'DELETE', 'id': track_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)


class LikeSetAPIView(GenericAPIView):

    serializer_class = serializers.Serializer
    lookup_field = 'set_id'

    def post(self, request, set_id=None):
        service = LikeService(context={'user': request.user, 'type': 'set', 'method': 'POST', 'id': set_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)

    def delete(self, request, set_id=None):
        service = LikeService(context={'user': request.user, 'type': 'set', 'method': 'DELETE', 'id': set_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)


class RepostTrackAPIView(GenericAPIView):

    serializer_class = serializers.Serializer
    lookup_field = 'track_id'

    def post(self, request, track_id=None):
        service = RepostService(context={'user': request.user, 'type': 'track', 'method': 'POST', 'id': track_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)

    def delete(self, request, track_id=None):
        service = RepostService(context={'user': request.user, 'type': 'track', 'method': 'DELETE', 'id': track_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)


class RepostSetAPIView(GenericAPIView):

    serializer_class = serializers.Serializer
    lookup_field = 'track_id'

    def post(self, request, set_id=None):
        service = RepostService(context={'user': request.user, 'type': 'set', 'method': 'POST', 'id': set_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)

    def delete(self, request, set_id=None):
        service = RepostService(context={'user': request.user, 'type': 'set', 'method': 'DELETE', 'id': set_id})
        service_status, data = service.execute()
        return Response(status=service_status, data=data)
