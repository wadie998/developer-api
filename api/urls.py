from django.urls import path

from .views import (
    ApiResponseView,
    AuthenticateView,
    JWTView,
    Service1View,
    Service2View,
)

urlpatterns = [
    path("service1", Service1View.as_view(), name="service1"),
    path("service2", Service2View.as_view(), name="service2"),
    path("jwt", JWTView.as_view(), name="jwt"),
    path("authenticate", AuthenticateView.as_view(), name="authenticate"),
    path("result", ApiResponseView.as_view(), name="result"),
]
