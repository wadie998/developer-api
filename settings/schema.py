from django.urls import path
from drf_spectacular.plumbing import build_root_object
from drf_spectacular.views import SpectacularAPIView
from rest_framework.response import Response


class CustomSpectacularAPIView(SpectacularAPIView):
    def get(self, request, *args, **kwargs):
        schema = build_root_object(None, request=request)
        schema_type = kwargs.get("url_name")

        if schema_type == "schema-internal" and not request.user.is_staff:
            # For internal schema, only allow admin users
            return Response({"detail": "Admin access required."}, status=403)

        return Response(schema)


urlpatterns = [
    path("api/schema/external/", CustomSpectacularAPIView.as_view(url_name="schema-external"), name="schema-external"),
    path("api/schema/internal/", CustomSpectacularAPIView.as_view(url_name="schema-internal"), name="schema-internal"),
]
