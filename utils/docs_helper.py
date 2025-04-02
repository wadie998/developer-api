from drf_spectacular.utils import OpenApiParameter

CUSTOM_AUTHENTICATION = OpenApiParameter(
    name="AUTHORIZATION",
    description="Authorization token",
    required=True,
    type=str,
    location=OpenApiParameter.HEADER,
)
