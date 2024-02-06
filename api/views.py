import logging

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from settings.settings import GC_LOGS_CRONJOBS_CHANNEL_WEBHOOK, PROJECT_DOMAIN
from utils.api_keys_manager import HasService1ApiKey, HasService2ApiKey
from utils.decorators import IsValidGenericApi
from utils.google_chat_logs import generate_gc_card_body
from utils.jwt_helpers import generate_token
from utils.signature_manager import verify_password_with_hash

from .models.models import JhiUser
from .pagination import ModelPagination
from .permissions import IsAuthenticated, IsBackendAuthenticated
from .serializer import ApiResponseViewSerializer, AuthenticateSerializer

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
class ApiResponseView(GenericAPIView):
    pagination_class = ModelPagination
    serializer_class = ApiResponseViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Example queryset
        from .models.models import JhiUser

        return JhiUser.objects.all().order_by("id")

    def get_paginated_link(self, page_obj):
        base_url = PROJECT_DOMAIN + reverse("result")
        links = []
        if page_obj.has_next():
            links.append(f'<{base_url}?page={page_obj.next_page_number()}>; rel="next"')
        if page_obj.has_previous():
            links.append(f'<{base_url}?page={page_obj.previous_page_number()}>; rel="prev"')
        links.append(f'<{base_url}?page={page_obj.paginator.page_range[-1]}>; rel="last"')
        links.append(f'<{base_url}?page=1>; rel="first"')

        return ", ".join(links)

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sort_param = serializer.validated_data.get("sort", None)
        page_param = serializer.validated_data.get("page", 1)
        size_param = serializer.validated_data.get("size", 10)
        filter_param = serializer.validated_data.get("filter_field", None)
        queryset = self.get_queryset()

        # Sorting
        if sort_param:
            sort_field, sort_order = sort_param.split(",")
            if sort_order == "desc":
                sort_field = f"-{sort_field}"
            queryset = queryset.order_by(sort_field)

        # Filtering by account
        if filter_param:
            queryset = queryset.filter(filter_param=filter_param)

        # Pagination
        paginated_queryset = Paginator(queryset, size_param)
        page_obj = paginated_queryset.get_page(page_param)
        data = list(page_obj.object_list.values())
        # Adding custom headers to response
        headers = {
            "x-total-count": paginated_queryset.count,
            "link": self.get_paginated_link(page_obj),
        }
        return Response(
            data={"result": data, "code": 0, "name": "projectmanager"}, headers=headers, status=status.HTTP_200_OK
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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        try:
            user = JhiUser.objects.get(login=username)
        except ObjectDoesNotExist:
            return Response(
                data={"title": "Unauthorized", "detail": "Bad credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        password = str(serializer.validated_data.get("password")).encode("utf-8")
        if not verify_password_with_hash(password, user.password_hash.encode("utf-8")):
            return Response(
                data={"title": "Unauthorized", "detail": "Bad credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        token = generate_token(str(username), str(password), user.id)
        return Response(data={"id_token": token}, status=status.HTTP_200_OK)
