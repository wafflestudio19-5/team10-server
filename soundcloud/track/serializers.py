from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound, NotAuthenticated
from datetime import datetime
from soundcloud.exceptions import ConflictError
from track.models import Track
from comment.models import Comment
from user.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    writer = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'writer',
            'content',
            'created_at',
            'commented_at',
            'parent_comment'
        )


class PostCommentService(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=True, allow_null=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def execute(self):
        self.is_valid(raise_exception=True)

        user = self.context['request'].user
        if not user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        track_id = self.context['track_id']
        track = get_object_or_404(Track, id=track_id)
        content = self.validated_data.get('content')
        parent_comment_id = self.validated_data.get('parent_id')
        parent_comment = get_object_or_404(Comment, id=parent_comment_id) if parent_comment_id else None
        if parent_comment and Comment.objects.filter(writer=user, track=track, parent_comment=parent_comment):
            raise ConflictError("Comment already exists on this parent.")

        Comment.objects.create(writer=user,
                               track=track,
                               content=content,
                               commented_at=datetime.now(),
                               parent_comment=parent_comment)

        return status.HTTP_201_CREATED, "Comment created."


class DeleteCommentService(serializers.Serializer):
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def execute(self):
        self.is_valid(raise_exception=True)

        user = self.context['request'].user
        if not user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")
        current_comment = self.context['comment']
        parent_comment_id = self.validated_data.get('parent_id')
        parent_comment = get_object_or_404(Comment, id=parent_comment_id) if parent_comment_id else None

        if current_comment.parent_comment != parent_comment:
            raise NotFound("Comment with given parent id does not exist.")

        child_comment = current_comment.reply
        current_comment.delete()
        if child_comment:
            child_comment.parent_comment = parent_comment
            child_comment.save()

        return status.HTTP_200_OK, "Comment deleted."


class RetrieveCommentService(serializers.Serializer):

    def execute(self):
        track_id = self.context['track_id']
        track = get_object_or_404(Track, id=track_id)
        comments = Comment.objects.filter(track=track)

        return status.HTTP_200_OK, comments
