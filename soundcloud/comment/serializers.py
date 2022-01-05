from rest_framework import serializers
from rest_framework.serializers import ValidationError
from comment.models import Comment
from track.serializers import CommentTrackSerializer
from user.serializers import SimpleUserSerializer


class TrackCommentSerializer(serializers.ModelSerializer):

    writer = SimpleUserSerializer(read_only=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'content',
            'created_at',
            'commented_at',
            'parent_id',
            'parent_comment',
            'children',
        )
        read_only_fields = (
            'created_at',
            'commented_at',
            'parent_comment',
        )

    def validate_parent_id(self, value):
        try:
            parent_comment = self.context['queryset'].get(id=value)
        except Comment.DoesNotExist:
            raise ValidationError("Parent comment id does not exist on the track.")

        if self.context['queryset'].filter(parent_comment=parent_comment).exists():
            raise ValidationError("Comment already exists on this parent.")

        self.context['parent_comment'] = parent_comment

        return value

    def validate(self, data):
        data['writer'] = self.context['request'].user
        data['track'] = self.context['track']
        parent_id = data.pop('parent_id', None)
        if parent_id is not None:
            data['parent_comment'] = self.context.get('parent_comment')

        return data

    def get_children(self, comment):
        replies = []
        child_comment = getattr(comment, 'reply', None)
        while child_comment:
            replies.append(child_comment.id)
            child_comment = getattr(child_comment, 'reply', None)
        return SimpleTrackCommentSerializer(Comment.objects.filter(id__in=replies), many=True).data

    def delete(self):
        current_comment = self.instance
        parent_comment = getattr(current_comment, 'parent_comment', None)
        child_comment = getattr(current_comment, 'reply', None)
        current_comment.delete()

        if child_comment:
            child_comment.parent_comment = parent_comment
            child_comment.save()


class SimpleTrackCommentSerializer(serializers.ModelSerializer):
    writer = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'content',
            'created_at',
            'commented_at',
            'parent_comment',
        )


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
