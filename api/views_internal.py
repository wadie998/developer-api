import logging

from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import FlouciApp
from api.permissions import IsFlouciAuthenticated
from api.serializers import CheckUserExistsSerializer, CreateDeveloperAccountSerializer
from settings.settings import DJANGO_SERVICE_VERSION
from utils.api_keys_manager import HasBackendApiKey
from utils.decorators import IsValidGenericApi

logger = logging.getLogger(__name__)


@extend_schema(exclude=True)
@IsValidGenericApi(post=False, get=True)
class CheckUserExistsView(GenericAPIView):
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)
    serializer_class = CheckUserExistsSerializer

    def get(self, request, serializer):
        tracking_id = serializer.validated_data.get("tracking_id")
        user_exists = FlouciApp.objects.filter(tracking_id=tracking_id).exists()
        if not user_exists:
            return Response(
                {"success": False, "result": {"message": "User has no developer account"}},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        return Response({"success": True, "result": {"message": "User exists"}}, status=status.HTTP_200_OK)


# NO LONGER NEEDED POST MIGRATION
@extend_schema(exclude=True)
@IsValidGenericApi()
class CreateDeveloperAccountView(GenericAPIView):
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)
    serializer_class = CreateDeveloperAccountSerializer

    def post(self, request, serializer):
        if not request.tracking_id:
            # From backend
            request.tracking_id = serializer.validated_data.get("login")
        user_exists = FlouciApp.objects.filter(tracking_id=request.tracking_id).exists()
        if user_exists:
            return JsonResponse(
                {"success": False, "message": "User exists.", "result": "NA"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        FlouciApp.objects.create(
            tracking_id=request.tracking_id,
            name="TEST APP",
            description="This is your test app",
            wallet="Test wallet",
            test=True,
            merchant_id=0,
        )
        return Response(
            {
                "result": "account_created",
                "name": "developer_account",
                "version": DJANGO_SERVICE_VERSION,
            },
            status=status.HTTP_201_CREATED,
        )
