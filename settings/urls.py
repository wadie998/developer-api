"""
URL configuration for django-template-app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import include
from django.urls import path
from django_otp.admin import OTPAdminSite
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from settings.settings import ADMIN_ENABLED, ADMIN_TWO_FA_ENABLED

urlpatterns = [
    path("api/ht", include("health_check.urls")),
    path("api/", include("api.urls"), name="api"),
    path("partners/", include("partners.urls"), name="partner_api"),
    # SCHEMA PUBLIC
    path("api/schema/public", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


if ADMIN_ENABLED:
    from django.contrib import admin

    if ADMIN_TWO_FA_ENABLED:
        admin.site.__class__ = OTPAdminSite
    urlpatterns += [path("admin/", admin.site.urls)]
