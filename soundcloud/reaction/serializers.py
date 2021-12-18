from rest_framework import serializers
from reaction.models import Like, Repost


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        field = '__all__'

    def validate(self, data):
        
        return data

class RepostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repost
        field = '__all__'

    def validate(self, data):
        
        return data
