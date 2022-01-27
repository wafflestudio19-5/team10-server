from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, extend_schema


resolve_schema = extend_schema(
    summary="Resolves soundwaffle.com URLs to Resource URLs to use with the API.",
    parameters=[
        OpenApiParameter(
            name="url",
            type=str,
            location=OpenApiParameter.QUERY,
            description="soundwaffle.com URL",
            required=True,
        )
    ],
    responses={
        302: OpenApiResponse(description='Found'),
        400: OpenApiResponse(description='Bad Request'),
        404: OpenApiResponse(description='Not Found'),
    }
)
