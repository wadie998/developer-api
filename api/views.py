from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from utils.api_keys_manager import HasService1ApiKey, HasService2ApiKey

from .permissions import IsJWTAuthenticated


class Service1View(GenericAPIView):
    permission_classes = [HasService1ApiKey]

    def get(self, request):
        return Response(data={"name": "service1"})


class Service2View(GenericAPIView):
    permission_classes = [HasService2ApiKey]

    def get(self, request):
        return Response(data={"name": "service2"})


class JWTView(GenericAPIView):
    permission_classes = [IsJWTAuthenticated]

    def get(self, request):
        return Response(data={"name": "jwt"})
