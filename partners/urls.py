from django.urls import path

from api.views_public import SendMoneyView
from partners.views import (
    AuthenticateView,
    BalanceView,
    ConfirmLinkAccountView,
    HistoryView,
    InitiateLinkAccountView,
    InitiatePaymentView,
    RefreshAuthenticateView,
)
from partners.webhook_catchers import SendMoneyDeveloperApiCatcher

urlpatterns = [
    # path("partners/accounts/is_flouci", IsFlouciView.as_view(), name="partner_is_flouci"),
    path("accounts/initiate_link_account", InitiateLinkAccountView.as_view(), name="partner_initiate_link_account"),
    path("accounts/confirm_link_account", ConfirmLinkAccountView.as_view(), name="partner_confirm_link_account"),
    path("accounts/authenticate", AuthenticateView.as_view(), name="partner_authenticate"),
    path("accounts/authenticate/refresh", RefreshAuthenticateView.as_view(), name="partner_refresh_authenticate"),
    path("transactions/balance", BalanceView.as_view(), name="partner_balance"),
    path("transactions/history", HistoryView.as_view(), name="partner_history"),
    path("transactions/initiate_payment", InitiatePaymentView.as_view(), name="partner_initiate_payment"),
    path("transactions/send_money", SendMoneyView.as_view(), name="partner_send_money"),
    path(
        "internal/send_money_catcher",
        SendMoneyDeveloperApiCatcher.as_view(),
        name="partner_send_money_catcher",
    ),
]
