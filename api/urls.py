from django.urls import path

from api.views_developer_auth import (
    CreateDeveloperAppView,
    GetDeveloperAppDetailsView,
    GetDeveloperAppMetricsView,
    GetDeveloperAppOrdersView,
    RevokeDeveloperAppView,
)
from api.views_internal import CheckUserExistsView, CreateDeveloperAccountView
from api.views_public import (
    CheckSendMoneyStatusView,
    GeneratePaymentView,
    SendMoneyView,
    VerifyPaymentView,
)

urlpatterns = [
    # urls with developer app authentication (public)
    path("generate_payment", GeneratePaymentView.as_view(), name="generate_payment"),
    path("verify_payment/<str:payment_id>", VerifyPaymentView.as_view(), name="verify_payment"),
    path("send_money", SendMoneyView.as_view(), name="send_money"),
    path("check_send_money_status", CheckSendMoneyStatusView.as_view(), name="check_send_money_status"),
    # urls with jhipster authentication
    # path("authenticate", AuthenticateView.as_view(), name="authenticate"), # TO depricate
    # urls with backend authentication
    path(
        "internal/checkuserexists/<str:tracking_id>", CheckUserExistsView.as_view(), name="check_user_exists"
    ),  # Tested
    path("internal/register", CreateDeveloperAccountView.as_view(), name="create_developer_account"),  # Tested
    # urls with either jhipster or backend authentication
    path("apps", CreateDeveloperAppView.as_view(), name="create_developer_app"),  # to depricate
    path("internal/apps", CreateDeveloperAppView.as_view(), name="create_developer_app_internal"),
    path("internal/apps/<uuid:app_id>", GetDeveloperAppDetailsView.as_view(), name="get_developer_app_details"),
    path("internal/apps/<uuid:app_id>/revoke", RevokeDeveloperAppView.as_view(), name="get_developer_app_details"),
    # TODO depricate these views, and return empty fields
    path("internal/metrics/<uuid:app_id>", GetDeveloperAppMetricsView.as_view(), name="get_developer_app_details"),
    path("internal/orders/<uuid:app_id>", GetDeveloperAppOrdersView.as_view(), name="get_developer_app_details"),
]
