import requests
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from settings.settings import GC_LOGS_CRONJOBS_CHANNEL_WEBHOOK
from utils.api_keys_manager import HasService1ApiKey, HasService2ApiKey

from .permissions import IsAuthenticated, IsBackendAuthenticated
from .serializer import AuthenticateSerializer


class Service1View(GenericAPIView):
    permission_classes = [HasService1ApiKey]

    def get(self, request):
        return Response(data={"name": "service1"})


class Service2View(GenericAPIView):
    permission_classes = [HasService2ApiKey]

    def get(self, request):
        return Response(data={"name": "service2"})


class ApiResponseView(GenericAPIView):
    def get(self, request):
        return Response(data={"result": {}, "code": 0, "name": "projectmanager"}, status=status.HTTP_200_OK)


class JWTView(GenericAPIView):
    permission_classes = [IsBackendAuthenticated]

    def get(self, request):
        requests.post(GC_LOGS_CRONJOBS_CHANNEL_WEBHOOK, json={"text": "Testing django project webhook"})
        return Response(data={"name": "jwt"})


class AuthenticateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuthenticateSerializer

    def post(self, request):
        return Response(data={"authenticate": "True"})
