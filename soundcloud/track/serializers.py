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


class CommentService(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=False)

    def post(self):
        self.is_valid(raise_exception=True)

        user = self.context['request'].user
        if not user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")

        track = self.context['track']
        content = self.validated_data.get('content')
        parent_comment_id = self.data.get('parent_id')
        parent_comment = get_object_or_404(Comment, id=parent_comment_id) if parent_comment_id else None

        Comment.objects.create(writer=user,
                               track=track,
                               content=content,
                               commented_at=datetime.now(),
                               parent_comment=parent_comment)

        return status.HTTP_201_CREATED, "Comment created."

    def delete(self):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise NotAuthenticated("먼저 로그인 하세요.")

        track = self.context['track']
        parent_comment_id = self.data.get('parent_id')
        parent_comment = get_object_or_404(Comment, id=parent_comment_id) if parent_comment_id else None

        try:
            current = Comment.objects.get(writer=user, track=track, parent_comment=parent_comment)
            child = Comment.objects.filter(parent_comment=current)
            if child:
                child[0].parent_comment = parent_comment
            current.delete()
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        return status.HTTP_200_OK, "Comment deleted."

    def retrieve(self):
        track = self.context['track']
        comments = Comment.objects.filter(track=track)

        return status.HTTP_200_OK, comments
