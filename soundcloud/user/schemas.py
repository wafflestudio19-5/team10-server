from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from comment.serializers import UserCommentSerializer
from set.serializers import SimpleSetSerializer
from track.serializers import SimpleTrackSerializer, UserTrackSerializer
from user.serializers import *


auth_signup_schema = extend_schema(
    summary="Signup",
    tags=['auth', ],
    responses={
        201: OpenApiResponse(response=UserCreateSerializer, description='Created'),
        400: OpenApiResponse(description='Bad Request'),
        409: OpenApiResponse(description='Conflict'),
    }
)

auth_login_schema = extend_schema(
    summary="Login",
    tags=['auth', ],
    responses={
        200: OpenApiResponse(response=UserLoginSerializer, description='OK'),
        400: OpenApiResponse(description='Bad Request'),
    }
)

auth_logout_schema = extend_schema(
    summary="Logout",
    tags=['auth', ],
    description="Do nothing, actually.",
    responses={
        200: OpenApiResponse(description='OK'),
        401: OpenApiResponse(description='Unauthorized'),
    }
)

users_viewset_schema = extend_schema_view(
    retrieve=extend_schema(
        summary="Retrieve User",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    list=extend_schema(
        summary="List Users",
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer, description='OK'),
        }
    ),
    followers=extend_schema(
        summary="Get User's Followers",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    followings=extend_schema(
        summary="Get User's Followings",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    tracks=extend_schema(
        summary="Get User's Tracks",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=UserTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    sets=extend_schema(
        summary="Get User's sets",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    history_tracks=extend_schema(
        summary="Get User's Track History",
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    history_sets=extend_schema(
        summary="Get User's Set History",
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    likes_tracks=extend_schema(
        summary="Get User's Liked Tracks",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    reposts_tracks=extend_schema(
        summary="Get User's Reposted Tracks",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleTrackSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    likes_sets=extend_schema(
        summary="Get User's Liked Sets",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    reposts_sets=extend_schema(
        summary="Get User's Reposted Sets",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
    comments=extend_schema(
        summary="Get User's Comments",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            200: OpenApiResponse(response=UserCommentSerializer(many=True), description='OK'),
            404: OpenApiResponse(description='Not Found'),
        }
    ),
)

users_self_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve Me",
        responses={
            200: OpenApiResponse(response=UserSerializer, description='OK'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    put=extend_schema(
        summary="Update Me",
        responses={
            200: OpenApiResponse(response=UserMediaUploadSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    patch=extend_schema(
        summary="Partial Update Me",
        responses={
            200: OpenApiResponse(response=UserMediaUploadSerializer, description='OK'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
)

users_follow_schema = extend_schema_view(
  post=extend_schema(
      summary="Follow User",
      responses={
          201: OpenApiResponse(description='Created'),
          400: OpenApiResponse(description='Bad Request'),
          401: OpenApiResponse(description='Unauthorized'),
          404: OpenApiResponse(description='Not Found'),
      }
  ),
  delete=extend_schema(
      summary="Unfollow User",
      responses={
          204: OpenApiResponse(description='No Content'),
          400: OpenApiResponse(description='Bad Request'),
          401: OpenApiResponse(description='Unauthorized'),
          404: OpenApiResponse(description='Not Found'),
      }
  ),
)
