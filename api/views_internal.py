import logging
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import App, JhiUser
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
        if request.tracking_id and request.tracking_id != tracking_id:
            return Response({"success": False, "result": {"message": "bad input"}}, status=status.HTTP_200_OK)
        try:
            JhiUser.objects.get(login=tracking_id)
            return Response({"success": True, "result": {"message": "User exists"}}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"success": False, "result": {"message": "User has no developer account"}},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        # except JhiUser.DoesNotExist:
        #     return JsonResponse({"success": False, "details": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # res = requests.get(
        #     FLOUCI_DEVELOPER_API_IP + "/api/internal/checkuserexists/" + individual.get_phone_number(),
        #     headers={"Content-Type": "application/json", "api-key": FLOUCI_DEVELOPER_API_KEY},
        # )

        # res = requests.get(
        # #     FLOUCI_DEVELOPER_API_IP + "/api/internal/checkuserexists/" + individual.get_phone_number(),
        # #     headers={"Content-Type": "application/json", "api-key": FLOUCI_DEVELOPER_API_KEY},
        # # )
        # created = True
        # user = JhiUser.objects.create(
        #     id=1234, # add auto to db and remove this field
        #     login=request.tracking_id,
        #     password_hash=request.tracking_id, # TODO create random generate password function
        #     activated=True,
        #     email_validated=True,
        #     deleted=False,
        #     created_by="system",
        #     created_date=timezone.now()
        # )
        # print("hi")
        # if created:
        #     try:
        #         old_apps_to_migrate = App.objects.filter(user__login=phone_number_or_tracking_id)
        #         for app in old_apps_to_migrate:
        #             # TODO migrate old apps in the first log in with tracking_id
        #             print(f"{app.name} should be migrated")
        #     except ObjectDoesNotExist:
        #         old_apps_to_migrate = []

        # if res.status_code == 200:
        #     return JsonResponse({"success": True, "result": res.json()["result"]}, status=status.HTTP_200_OK)
        # else:
        #     logger.warning("Problem in CheckUserExistsView, details: %s ", res.json())
        #     return JsonResponse({"success": False, "details": res.json()}, status=res.status_code)


# NO LONGER NEEDED POST MIGRATION
@extend_schema(exclude=True)
@IsValidGenericApi()
class CreateDeveloperAccountView(GenericAPIView):
    permission_classes = (HasBackendApiKey | IsFlouciAuthenticated,)
    serializer_class = CreateDeveloperAccountSerializer

    def post(self, request, serializer):
        try:
            if not request.tracking_id:
                # From backend
                request.tracking_id = serializer.validated_data.get("login")
            print("heere")
            print(request.tracking_id)
            try:
                JhiUser.objects.get(login=request.tracking_id)
                return JsonResponse(
                    {"success": False, "message": "User exists.", "result": "NA"},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )
            except ObjectDoesNotExist:
                user, _ = JhiUser.objects.get_or_create(
                    login=request.tracking_id,
                    password_hash=request.tracking_id,  # TODO create random generate password function
                    activated=True,
                    email_validated=True,
                    deleted=False,
                    created_by="system",
                    created_date=timezone.now(),
                )
                if user:
                    App.objects.create(
                        user=user,
                        name="TEST APP",
                        description="This is your test app",
                        public_token=uuid.uuid4(),
                        private_token=uuid.uuid4(),
                        app_id=uuid.uuid4(),
                        wallet="Test wallet",
                        status="VERIFIED",
                        active=True,
                        test=True,
                        deleted=False,
                        date_created=timezone.now(),
                        merchant_id=0,
                    )
            return Response(
                {
                    "result": "account_created",
                    "code": 201,
                    "name": "developer_account",
                    "version": DJANGO_SERVICE_VERSION,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(e)
