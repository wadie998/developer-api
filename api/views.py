import logging

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from settings.settings import GC_LOGS_CRONJOBS_CHANNEL_WEBHOOK
from utils.api_keys_manager import (
    HasBackendApiKey,
    HasService1ApiKey,
    HasService2ApiKey,
)
from utils.custom_exceptions import CustomJhipsterxception
from utils.decorators import IsValidGenericApi
from utils.google_chat_logs import generate_gc_card_body
from utils.jwt_helpers import generate_token
from utils.signature_manager import verify_password_with_hash

from .models.model import JhiUser
from .pagination import (
    ZeroBasedPagination,
    generate_pagination_data,
    generate_pagination_links,
)
from .permissions import HasJhipsterKey, IsBackendAuthenticated
from .serializer import ApiResponseViewSerializer, AuthenticateSerializer, JhiSerializer

logger = logging.getLogger(__name__)


class Service1View(GenericAPIView):
    permission_classes = [HasService1ApiKey]

    def get(self, request):
        return Response(data={"result": {"name": "service1"}, "code": 0, "name": "projectmanager"})


class Service2View(GenericAPIView):
    permission_classes = [HasService2ApiKey]

    def get(self, request):
        return Response(data={"result": {"name": "service2"}, "code": 0, "name": "projectmanager"})


@IsValidGenericApi(get=True, post=False)
class BaseRequestView(GenericAPIView):
    pagination_class = ZeroBasedPagination
    serializer_class = ApiResponseViewSerializer
    permission_classes = [HasBackendApiKey | HasJhipsterKey]

    def get_queryset(self):
        queryset = self.apply_additional_filters(queryset=None)
        queryset = self.apply_common_filters(queryset)
        return queryset

    def apply_common_filters(self, queryset):
        # Retrieve filter parameters from request
        filter_param = self.request.query_params.get("filter_param")
        sort_param = self.request.query_params.get("sort")

        # Sorting
        if sort_param:
            sort_field, sort_order = sort_param.split(",")
            if sort_order == "desc":
                sort_field = f"-{sort_field}"
            queryset = queryset.order_by(sort_field)

        # Apply common filtering logic
        if filter_param:
            queryset = queryset.filter(field_to_filter=filter_param)

        return queryset

    def apply_additional_filters(self, queryset):
        if not queryset:
            raise NotImplementedError("Subclasses must implement get_queryset method.")
        return queryset

    def get(self, request, serializer):
        sort_param = serializer.validated_data.get("sort", None)
        queryset = self.get_queryset()
        queryset_page = self.paginate_queryset(queryset)
        pagination_headers, pagination_data, serialized_data = None, None, []
        if queryset_page:
            pagination_headers = generate_pagination_links(
                request, self.paginator.page.paginator, self.paginator.page.number
            )
            pagination_data = generate_pagination_data(self.paginator.page)
            serialized_data = JhiSerializer(instance=queryset_page, many=True).data
        result = {}
        result["content"] = serialized_data
        result["sort"] = {
            "empty": True if not sort_param else False,
            "sorted": bool(sort_param),
            "unsorted": True if not sort_param else False,
        }

        if pagination_data:
            result.update(pagination_data)
        return Response(
            data={"result": result, "code": 200, "name": "Jhimanager"},
            status=status.HTTP_200_OK,
            headers=pagination_headers,
        )


class JWTView(GenericAPIView):
    permission_classes = [IsBackendAuthenticated]

    def get(self, request):
        gc_card = generate_gc_card_body(self.__class__.__name__, "No error just testing the format")
        requests.post(GC_LOGS_CRONJOBS_CHANNEL_WEBHOOK, json=gc_card)
        return Response(data={"name": "jwt"})


@IsValidGenericApi()
class AuthenticateView(GenericAPIView):
    serializer_class = AuthenticateSerializer

    def post(self, request, serializer):
        username = serializer.validated_data.get("username")
        try:
            user = JhiUser.objects.get(login=username)
        except ObjectDoesNotExist:
            raise CustomJhipsterxception(
                "Unauthorized",
                "Bad credentials",
                status.HTTP_401_UNAUTHORIZED,
                path="/api/authenticate",
                message="error.http.401",
            )
        password = str(serializer.validated_data.get("password")).encode("utf-8")
        if not verify_password_with_hash(password, user.password_hash.encode("utf-8")):
            raise CustomJhipsterxception(
                "Unauthorized",
                "Bad credentials",
                status.HTTP_401_UNAUTHORIZED,
                path="/api/authenticate",
                message="error.http.401",
            )
        token = generate_token(str(username), user.get_user_authority_role())
        headers = {"authorization": f"Bearer {token}"}
        return JsonResponse(data={"id_token": token}, headers=headers, status=status.HTTP_200_OK)
