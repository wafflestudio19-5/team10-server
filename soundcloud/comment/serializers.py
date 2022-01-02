from rest_framework import serializers
from rest_framework.serializers import ValidationError
from comment.models import Comment
from user.serializers import SimpleUserSerializer


class CommentSerializer(serializers.ModelSerializer):
    writer = SimpleUserSerializer(read_only=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

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

        return value

    def validate(self, data):
        data['writer'] = self.context['request'].user
        data['track'] = self.context['track']

        parent_id = data.pop('parent_id', None)
        if parent_id is not None:
            data['parent_comment'] = self.context['queryset'].get(id=parent_id)

        return data

    def delete(self):
        current_comment = self.instance
        parent_comment = getattr(current_comment, 'parent_comment', None)
        child_comment = getattr(current_comment, 'reply', None)
        current_comment.delete()

        if child_comment:
            child_comment.parent_comment = parent_comment
            child_comment.save()
