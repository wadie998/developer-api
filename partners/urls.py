from django.urls import path

from partners.views import (
    AuthenticateView,
    BalanceView,
    ConfirmLinkAccountView,
    FetchGPSTransactionStatusView,
    HistoryView,
    InitiateLinkAccountView,
    InitiatePaymentView,
    InitiatePosTransaction,
    IsFlouciView,
    PartnerBalanceView,
    PartnerHistoryView,
    PartnerInitiatePaymentView,
    PartnerSendMoneyView,
    RefreshAuthenticateView,
)
from partners.webhook_catchers import SendMoneyDeveloperApiCatcher

urlpatterns = [
    path("accounts/initiate_link_account", InitiateLinkAccountView.as_view(), name="partner_initiate_link_account"),
    path("accounts/confirm_link_account", ConfirmLinkAccountView.as_view(), name="partner_confirm_link_account"),
    # ENDPOINTS USED BY AUTHENTICATING THE CLIENT WITH PARTNER FIRST
    path("accounts/is_flouci", IsFlouciView.as_view(), name="is_flouci"),
    path("accounts/authenticate", AuthenticateView.as_view(), name="partner_authenticate"),
    path("accounts/authenticate/refresh", RefreshAuthenticateView.as_view(), name="partner_refresh_authenticate"),
    path("transactions/balance", BalanceView.as_view(), name="partner_balance"),
    path("transactions/history", HistoryView.as_view(), name="partner_history"),
    path("transactions/initiate_payment", InitiatePaymentView.as_view(), name="partner_initiate_payment"),
    # Money transfer
    path("transactions/send_money", PartnerSendMoneyView.as_view(), name="partner_send_money"),
    path(
        "internal/send_money_catcher",
        SendMoneyDeveloperApiCatcher.as_view(),
        name="partner_send_money_catcher",
    ),
    # ENDPOINTS USED BY PARTNER TO ISSUE DIRECTLY THE PAYMENT REQUEST
    path("v1/transactions/balance", PartnerBalanceView.as_view(), name="v1_partner_balance"),
    path("v1/transactions/history", PartnerHistoryView.as_view(), name="v1_partner_history"),
    path("v1/transactions/initiate_payment", PartnerInitiatePaymentView.as_view(), name="v1_partner_initiate_payment"),
    # External services, POS integration
    path("transactions/init_pos_transaction", InitiatePosTransaction.as_view(), name="init_pos_transaction"),
    # Fetch GPS transaction status
    path(
        "transactions/fetch_gps_transaction_status",
        FetchGPSTransactionStatusView.as_view(),
        name="fetch_gps_transaction_status",
    ),
]
