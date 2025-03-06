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
    AcceptPayment,
    AcceptPaymentV2,
    CheckSendMoneyStatusView,
    CheckSendMoneyStatusViewV2,
    GeneratePaymentView,
    GeneratePaymentViewV2,
    GeneratePaymentWordpressView,
    GeneratePaymentWordpressViewV2,
    SendMoneyView,
    SendMoneyViewV2,
    VerifyPaymentView,
    VerifyPaymentViewV2,
)

urlpatterns = [
    # urls with developer app authentication (public)
    path("accept", AcceptPayment.as_view(), name="accept"),
    path("v2/accept", AcceptPaymentV2.as_view(), name="accept_v2"),
    path("generate_payment", GeneratePaymentView.as_view(), name="generate_payment"),
    path("v2/generate_payment", GeneratePaymentViewV2.as_view(), name="generate_payment_v2"),
    path("generate_payment/wordpress", GeneratePaymentWordpressView.as_view(), name="generate_payment_wordpress"),
    path("v2/generate_payment/wordpress", GeneratePaymentWordpressViewV2.as_view(), name="generate_payment_v2"),
    path("verify_payment/<str:payment_id>", VerifyPaymentView.as_view(), name="verify_payment"),
    path("v2/verify_payment/<str:payment_id>", VerifyPaymentViewV2.as_view(), name="verify_payment_v2"),
    path("send_money", SendMoneyView.as_view(), name="send_money"),
    path("v2/send_money", SendMoneyViewV2.as_view(), name="send_money_v2"),
    path("check_payment_status/<uuid:operation_id>", CheckSendMoneyStatusView.as_view(), name="check_payment_status"),
    path(
        "v2/check_payment_status/<uuid:operation_id>",
        CheckSendMoneyStatusViewV2.as_view(),
        name="check_payment_status_v2",
    ),
    # urls with backend authentication
    path("internal/checkuserexists/<uuid:tracking_id>", CheckUserExistsView.as_view(), name="check_user_exists"),
    path("internal/register", CreateDeveloperAccountView.as_view(), name="create_developer_account"),
    # urls with either jhipster or backend authentication
    path("apps", CreateDeveloperAppView.as_view(), name="create_developer_app"),
    path("internal/apps", CreateDeveloperAppView.as_view(), name="create_developer_app_internal"),
    path(
        "internal/apps/<uuid:app_id>", GetDeveloperAppDetailsView.as_view(), name="get_developer_app_internal_details"
    ),
    path("internal/apps/<uuid:app_id>/revoke", RevokeDeveloperAppView.as_view(), name="revoke_developer_app"),
    # Depricated views
    path("internal/metrics/<uuid:app_id>", GetDeveloperAppMetricsView.as_view(), name="get_internal_metrics"),
    path("internal/orders/<uuid:app_id>", GetDeveloperAppOrdersView.as_view(), name="get_internal_orders"),
]
