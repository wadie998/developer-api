import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.response import Response

from api.models import FlouciApp
from api.permissions import IsFlouciAuthenticated, TokenPermission
from api.serializers import (
    AppCredsSerializer,
    CreateDeveloperAppSerializer,
    DefaultSerializer,
    DeveloperAppSerializer,
    GetDeveloperAppSerializer,
    UpdateDeveloperAppSerializer,
)
from settings.settings import DJANGO_SERVICE_VERSION
from utils.api_keys_manager import HasBackendApiKey
from utils.decorators import IsValidGenericApi
from utils.pagination_helper import generate_pagination_headers

logger = logging.getLogger(__name__)


@extend_schema(exclude=True)
@IsValidGenericApi(post=True, get=True, put=True)
class CreateDeveloperAppView(GenericAPIView):
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetDeveloperAppSerializer
        if self.request.method == "PUT":
            return UpdateDeveloperAppSerializer
        return CreateDeveloperAppSerializer

    def get(self, request, serializer):
        if not request.tracking_id:
            tracking_id = serializer.validated_data.get("tracking_id")
        else:
            tracking_id = request.tracking_id
        page = int(request.query_params.get("page", 0))
        size = int(request.query_params.get("size", 20))

        apps = FlouciApp.objects.filter(tracking_id=tracking_id)
        total_apps = apps.count()
        start = page * size
        end = start + size
        apps = apps[start:end]

        app_list = [app.get_app_details() for app in apps]
        base_url = request.build_absolute_uri(request.path)
        headers = generate_pagination_headers(base_url, page, size, total_apps)

        response = Response(
            {
                "result": app_list,
                "code": 200,
                "name": "developers",
                "total": total_apps,
                "page": page,
                "size": size,
                "version": DJANGO_SERVICE_VERSION,
            },
            status=status.HTTP_200_OK,
        )
        # Attach pagination headers
        for key, value in headers.items():
            response[key] = value

        return response

    def post(self, request, serializer):
        if not request.tracking_id:
            request.tracking_id = serializer.validated_data.get("username")
        elif request.tracking_id and not serializer.validated_data.get("username"):
            return Response(
                {"success": False, "details": "User not found."}, status=status.HTTP_412_PRECONDITION_FAILED
            )
        app = FlouciApp.objects.create(
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
            wallet=serializer.validated_data.get("wallet"),
            merchant_id=serializer.validated_data.get("merchant_id"),  # You might want to customize this
            tracking_id=request.tracking_id,
        )
        data = app.get_app_details()
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, serializer):
        id = serializer.validated_data.get("id")
        try:
            app = FlouciApp.objects.get(id=id)
        except FlouciApp.DoesNotExist:
            return Response({"detail": "App not found."}, status=status.HTTP_404_NOT_FOUND)
        updated_fields = []
        for field in ["name", "description"]:
            new_value = serializer.validated_data.get(field)
            if new_value is not None and getattr(app, field) != new_value:
                setattr(app, field, new_value)
                updated_fields.append(field)

        if updated_fields:
            app.save(update_fields=updated_fields)
        data = app.get_app_details()
        data["success"] = True
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(exclude=True)
class GetDeveloperAppDetailsView(ListCreateAPIView):
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)
    """
    returns:
    {
        "id": "eed87ffc-de9b-4c1d-b64f-9de6fa3c6d14",
        "name": "Test APP",
        "token": "38330adc-9891-40bc-8fb0-ef4b55060fdd",
        "secret": "cc983d84-1a11-4d20-b6fc-7b44e1867a38",
        "status": "VERIFIED",
        "active": true,
        "test": true,
        "date_created": "2023-08-08T17:46:42.224138+01:00",
        "description": "This is your test app",
        "transaction_number": 0,
        "gross": 0
    }
    """

    def get(self, request, id):
        try:
            apps = FlouciApp.objects.get(app_id=id)
        except FlouciApp.DoesNotExist:
            return Response({"detail": "App not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data=apps.get_app_details(), status=status.HTTP_200_OK)


@extend_schema(exclude=True)
@IsValidGenericApi(get=True, post=False)
class RevokeDeveloperAppView(GenericAPIView):
    """
    "result": {
        "id": "5fec121e-5ea2-46f7-9a3c-925fe6691be3",
        "name": "Sonaa amal",
        "token": "2e906bd0-bb43-494e-b1b2-f3b02fbd7ec7",
        "secret": "fd323fe0-277f-43ca-83b5-ba2541f0360b",
        "status": "VERIFIED",
        "active": true,
        "test": false,
        "date_created": "2023-10-19T15:53:27.305641+01:00",
        "description": "TAWA Digital",
        "transaction_number": 2,
        "gross": 109106
    },
    "code": 0,
    "message": "App revoked successfully: 4 revokes remaining for this month ",
    "name": "developers",
    "version": "4.4.91"
    """

    serializer_class = DeveloperAppSerializer
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)

    def get(self, request, serializer):
        id = serializer.validated_data.get("id")
        try:
            app = FlouciApp.objects.get(id=id)
        except FlouciApp.DoesNotExist:
            return Response({"detail": "App not found."}, status=status.HTTP_404_NOT_FOUND)
        app.revoke_keys()
        response_data = {
            "result": app.get_app_details(),
            "code": 0,
            "message": "App revoked successfully.",
            "name": "developers",
            "version": DJANGO_SERVICE_VERSION,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(exclude=True)
@IsValidGenericApi(get=True, post=False)
class EnableOrDisableDeveloperAppView(GenericAPIView):
    enable_or_disable = True
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)
    serializer_class = DeveloperAppSerializer

    def get(self, request, serializer):
        id = serializer.validated_data.get("id")
        try:
            app = FlouciApp.objects.get(id=id)
        except FlouciApp.DoesNotExist:
            return Response({"detail": "App not found."}, status=status.HTTP_404_NOT_FOUND)
        app.active = self.enable_or_disable
        app.save(update_fields=["active"])
        response_data = {
            "result": app.get_app_details(),
            "code": 0,
            "message": f"App {'enabled' if self.enable_or_disable else 'disabled'} successfully.",
        }
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(exclude=True)
# TODO Depricate View after removed from front
@IsValidGenericApi(post=False, get=True)
class GetDeveloperAppMetricsView(GenericAPIView):
    """
    {
        "result": [
            {
                "daily_metrics_id": "10f3e6a3-0e37-4d4b-b8c2-77bd34400a51",
                "transactions": 1760,
                "day": "2024-09-20",
                "amount_average": 9010880.681818182,
                "amount_sum": 15859150000,
                "fee_sum": 317183000,
                "fee_average": 180217.61363636365,
                "transaction_type": "SMT"
            },
            {
                "daily_metrics_id": "6ce4f520-aad3-46de-a5fd-8f52bec245f8",
                "transactions": 3,
                "day": "2024-09-20",
                "amount_average": 1.1910702E7,
                "amount_sum": 11910700,
                "fee_sum": 89300,
                "fee_average": 29766.0,
                "transaction_type": "DEVELOPER"
            },
        ],
        "code": 0,
        "message": "metrics for day 2024-09-20",
        "name": "developers",
        "version": "4.4.91"
    }
    """

    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)

    def get(self, request, app_id):
        response_data = {
            "result": [],
            "code": 0,
            "message": "Metrics for day",
            "name": "developers",
            "version": DJANGO_SERVICE_VERSION,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# TODO Depricate View after removed from front
@extend_schema(exclude=True)
@IsValidGenericApi(post=False, get=True)
class GetDeveloperAppOrdersView(GenericAPIView):
    """
    {result: [], code: 0, name: "data", version: "4.4.91"}
    """

    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)

    def get(self, request, app_id):
        response_data = {
            "result": [],
            "code": 0,
            "message": "metrics for day",
            "name": "developers",
            "version": DJANGO_SERVICE_VERSION,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@IsValidGenericApi(get=True, post=False)
class GetAppInfo(GenericAPIView):
    permission_classes = (TokenPermission,)
    serializer_class = DefaultSerializer

    def get(self, request, serializer):
        app = request.application
        response_data = {
            "result": app.get_app_info(),
            "code": 0,
            "name": "developers",
            "version": DJANGO_SERVICE_VERSION,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@IsValidGenericApi()
class PostAppInfo(GenericAPIView):
    serializer_class = AppCredsSerializer

    def post(self, request, serializer):
        app_token = serializer.validated_data.get("app_token")
        app_secret = serializer.validated_data.get("app_secret")
        try:
            app = FlouciApp.objects.get(public_token=app_token, private_token=app_secret)
        except FlouciApp.DoesNotExist:
            return Response(
                {"name": "developers", "version": DJANGO_SERVICE_VERSION, "message": "app not found", "code": 3},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code = 0
        if not app.active:
            code = 1
            logger.warning("Warning: App is disabled")
        if app.test:
            code = 2
            logger.warning("Warning: App is a test app")
        response_data = {
            "result": app.get_app_info(),
            "code": code,
            "name": "developers",
            "version": DJANGO_SERVICE_VERSION,
        }
        return Response(response_data, status=status.HTTP_200_OK)
