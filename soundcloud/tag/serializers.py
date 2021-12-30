from rest_framework import serializers
from tag.models import Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

    def validate(self, data):
        
        return data
