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
    CancelSMTPreAuthorization,
    CheckSendMoneyStatusView,
    ConfirmSMTPreAuthorization,
    GeneratePaymentView,
    SendMoneyView,
    VerifyPaymentView,
)

urlpatterns = [
    # urls with developer app authentication (public)
    path("accept", AcceptPayment.as_view(), name="accept"),
    path("generate_payment", GeneratePaymentView.as_view(), name="generate_payment"),
    path("generate_payment/wordpress", GeneratePaymentView.as_view(), name="generate_payment_wordpress"),
    path("verify_payment/<str:payment_id>", VerifyPaymentView.as_view(), name="verify_payment"),
    path("send_money", SendMoneyView.as_view(), name="send_money"),
    path("check_payment_status/<uuid:operation_id>", CheckSendMoneyStatusView.as_view(), name="check_payment_status"),
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
    path("confirm_transaction", ConfirmSMTPreAuthorization.as_view(), name="confirm_transaction"),
    path("cancel_transaction", CancelSMTPreAuthorization.as_view(), name="cancel_transaction"),
]
