from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiExample, extend_schema, extend_schema_view
from track.serializers import SimpleTrackSerializer, TrackSerializer, TrackMediaUploadSerializer
from user.serializers import SimpleUserSerializer


tracks_viewset_schema = extend_schema_view(
    create=extend_schema(
        summary="Create Track",
        responses={
            '201': OpenApiResponse(response=TrackMediaUploadSerializer, description='Created'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve Track",
        responses={
            '200': OpenApiResponse(response=TrackSerializer, description='OK'),
            '404': OpenApiResponse(description='Not Found')
        }
    ),
    update=extend_schema(
        summary="Update Track",
        responses={
            '200': OpenApiResponse(response=TrackMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    partial_update=extend_schema(
        summary="Partial Update Track",
        responses={
            '200': OpenApiResponse(response=TrackMediaUploadSerializer, description='OK'),
            '400': OpenApiResponse(description='Bad Request'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    destroy=extend_schema(
        summary="Delete Track",
        responses={
            '204': OpenApiResponse(description='No Content'),
            '401': OpenApiResponse(description='Unauthorized'),
            '403': OpenApiResponse(description='Permission Denied'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    list=extend_schema(
        summary="List Tracks",
        responses={
            '200': OpenApiResponse(response=SimpleTrackSerializer, description='OK'),
        }
    ),
    likers=extend_schema(
        summary="Get Track's Likers",
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
        summary="Get Track's Reposters",
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A page number within the paginated result set.'),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return per page.'),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
    hit=extend_schema(
        summary="Hit Track",
        parameters=[
            OpenApiParameter("set_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description='A set id containing the track.'),
        ],
        responses={
            '200': OpenApiResponse(description='OK'),
        }
    )
)

track_search_schema=extend_schema_view(
    get=extend_schema(
        summary="Search Track",
        parameters=[
            OpenApiParameter("text", OpenApiTypes.STR, OpenApiParameter.QUERY, description='Search text'),
            OpenApiParameter("ids[]", OpenApiTypes.OBJECT, OpenApiParameter.QUERY, description='A list of track ids to filter on',
                                 examples=[
                                    OpenApiExample(
                                        'Example',
                                        value=["1", "2", "3"]
                                    )
                                 ]
                             ),
            OpenApiParameter("genres[]", OpenApiTypes.OBJECT, OpenApiParameter.QUERY, description='A list of genres to filter on',
                                 examples=[
                                    OpenApiExample(
                                        'Example',
                                        value=["Pop", "House"]
                                    )
                                 ]
                             ),
            OpenApiParameter("created_at", OpenApiTypes.OBJECT, OpenApiParameter.QUERY, description='Return tracks created within the specified dates',
                                 examples=[
                                    OpenApiExample(
                                        'Example',
                                        value={
                                                  "from": "2020-12-24T00:00:00.000Z",
                                                  "to": "2022-12-24T00:00:00.000Z"
                                              }
                                    )
                                 ]
                             ),
        ],
        responses={
            '200': OpenApiResponse(response=SimpleUserSerializer(many=True), description='OK'),
            '404': OpenApiResponse(description='Not Found'),
        }
    ),
)