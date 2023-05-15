from django.urls import path
from .views import Service1View, Service2View, JWTView

urlpatterns = [
    path('service1', Service1View.as_view(), name="service1"),
    path('service2', Service2View.as_view(), name="service2"),
    path('jwt', JWTView.as_view(), name="jwt"),
]
