from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from comment.serializers import TrackCommentSerializer


comments_viewset_schema = extend_schema_view(
    create=extend_schema(
        summary="Create Comment",
        responses={
            201: OpenApiResponse(response=TrackCommentSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    list=extend_schema(
        summary="Get Comments on Track",
        responses={
            200: OpenApiResponse(response=TrackCommentSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    destroy=extend_schema(
        summary="Delete Comment",
        responses={
            204: OpenApiResponse(description='No Content'),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
)
