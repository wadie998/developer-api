from django.urls import path

from api.views_developer_auth import (
    CreateDeveloperAppView,
    EnableOrDisableDeveloperAppView,
    GetDeveloperAppDetailsView,
    GetDeveloperAppMetricsView,
    GetDeveloperAppOrdersView,
    RevokeDeveloperAppView,
)
from api.views_internal import CheckUserExistsView, CreateDeveloperAccountView
from api.views_public import (
    AcceptPayment,
    AcceptPaymentView,
    CancelSMTPreAuthorization,
    CheckSendMoneyStatusView,
    ConfirmSMTPreAuthorization,
    GeneratePaymentView,
    GeneratePaymentWordpressView,
    OldCheckSendMoneyStatusView,
    OldGeneratePaymentView,
    OldGeneratePaymentWordpressView,
    OldSendMoneyView,
    OldVerifyPaymentView,
    SendMoneyView,
    VerifyPaymentView,
)

urlpatterns = [
    # urls that start with Old are depricated onc
    path("accept", AcceptPayment.as_view(), name="old_accept_payment"),
    path("v2/accept", AcceptPaymentView.as_view(), name="accept_payment"),
    path("generate_payment", OldGeneratePaymentView.as_view(depricated=True), name="old_generate_payment"),
    path("v2/generate_payment", GeneratePaymentView.as_view(depricated=False), name="generate_payment"),
    path(
        "generate_payment/wordpress",
        OldGeneratePaymentWordpressView.as_view(depricated=True),
        name="old_generate_payment_wordpress",
    ),
    path(
        "v2/generate_payment/wordpress",
        GeneratePaymentWordpressView.as_view(depricated=False),
        name="generate_payment_wordpress",
    ),
    path("verify_payment/<str:payment_id>", OldVerifyPaymentView.as_view(), name="old_verify_payment"),
    path("v2/verify_payment/<str:payment_id>", VerifyPaymentView.as_view(), name="verify_payment"),
    path("send_money", OldSendMoneyView.as_view(), name="old_send_money"),
    path("v2/send_money", SendMoneyView.as_view(), name="send_money"),
    path(
        "check_payment_status/<uuid:operation_id>",
        OldCheckSendMoneyStatusView.as_view(),
        name="old_check_payment_status",
    ),
    path(
        "v2/check_payment_status/<uuid:operation_id>",
        CheckSendMoneyStatusView.as_view(),
        name="check_payment_status",
    ),
    # urls with backend authentication
    path("internal/checkuserexists/<uuid:tracking_id>", CheckUserExistsView.as_view(), name="check_user_exists"),
    path("internal/register", CreateDeveloperAccountView.as_view(), name="create_developer_account"),
    # urls with either jhipster or backend authentication
    path("apps", CreateDeveloperAppView.as_view(), name="create_developer_app"),
    path("internal/apps", CreateDeveloperAppView.as_view(), name="create_developer_app_internal"),
    path("apps/<uuid:id>", GetDeveloperAppDetailsView.as_view(), name="get_developer_app_details"),
    path("apps/<int:id>/revoke", RevokeDeveloperAppView.as_view(), name="revoke_developer_app"),
    path(
        "app/<int:id>/disable",
        EnableOrDisableDeveloperAppView.as_view(enable_or_disable=False),
        name="enable_developer_app",
    ),
    path(
        "app/<int:id>/enable",
        EnableOrDisableDeveloperAppView.as_view(enable_or_disable=True),
        name="disable_developer_app",
    ),
    # Depricated views
    path("metrics/<uuid:app_id>", GetDeveloperAppMetricsView.as_view(), name="get_internal_metrics"),
    path("orders/<uuid:app_id>", GetDeveloperAppOrdersView.as_view(), name="get_internal_orders"),
    # Pre-authorization endpoints
    path("confirm_payment", ConfirmSMTPreAuthorization.as_view(), name="confirm_payment"),
    path("cancel_payment", CancelSMTPreAuthorization.as_view(), name="cancel_payment"),
]
