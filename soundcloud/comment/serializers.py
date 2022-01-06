from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from comment.models import Comment, Group
from track.serializers import CommentTrackSerializer
from user.serializers import SimpleUserSerializer


class TrackCommentSerializer(serializers.ModelSerializer):

    writer = SimpleUserSerializer(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = (
            'id',
            'group',
            'writer',
            'content',
            'created_at',
            'commented_at',
        )
        read_only_fields = (
            'created_at',
            'commented_at',
        )

    def validate_group(self, value):
        if not Group.objects.filter(id=value.id, track=self.context['track']).exists():
            raise ValidationError(f"Group does not belong to {self.context['track']}.")

        return value

    def validate(self, data):
        data['writer'] = self.context['request'].user
        data['track'] = self.context['track']

        return data

    @transaction.atomic
    def delete(self):
        comment = self.instance
        group = comment.group
        comment.delete()

        if not group.comments.exists():
            group.delete()


class UserCommentSerializer(serializers.ModelSerializer):

    track = CommentTrackSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'track',
            'content',
            'created_at',
            'commented_at',
            'parent_comment',
        )
