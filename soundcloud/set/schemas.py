from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view, OpenApiTypes
from set.serializers import *

sets_viewset_schema = extend_schema_view( 
    list=extend_schema(
        summary="List of Sets",
        responses={
            200: OpenApiResponse(response=SimpleSetSerializer, description='OK'),
        }
    ),
    create=extend_schema(
        summary="Create Set",
        responses={
            201: OpenApiResponse(response=SetMediaUploadSerializer, description='Created'),
            400: OpenApiResponse(description='Bad Request'),
            401: OpenApiResponse(description='Unauthorized'),
        }
    ),
    update=extend_schema(
        summary="Update Set",
        responses={
            '200': OpenApiResponse(response=SetMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    partial_update=extend_schema(
        summary="Partial Update Set",
        responses={
            '200': OpenApiResponse(response=SetMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve Set",
        responses={
            '200': OpenApiResponse(response=SetSerializer, description='OK'),
            '404': OpenApiResponse(description='Not Found')
        }
    ),
    destroy=extend_schema(
        summary="Delete Set",
        responses={
            '204': OpenApiResponse(description='No Content'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    likers=extend_schema(
        summary="Get Set's Likers",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    reposters=extend_schema(
        summary="Get Set's Reposters",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    )
)

sets_track_schema=extend_schema( 
    summary="Add/Remove Track in Set",
    responses={
        '200': OpenApiResponse(description='OK'),
        '400': OpenApiResponse(description="Bad Request"),
        '401': OpenApiResponse(description='Unauthorized'),
        '403': OpenApiResponse(description='Permission Denied'),
        '404': OpenApiResponse(description='Not Found'),
    }
)
