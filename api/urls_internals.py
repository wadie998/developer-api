from django.urls import path

from api.views_internal import CheckUserExistsView, CreateDeveloperAccountView
from partners.webhook_catchers import SendMoneyDeveloperApiCatcher

urlpatterns = [
    # urls that start with Old are depricated onc
    path("checkuserexists/<uuid:tracking_id>", CheckUserExistsView.as_view(), name="internal_check_user_exists"),
    path("register", CreateDeveloperAccountView.as_view(), name="internal_create_developer_account"),
    path(
        "send_money_catcher",
        SendMoneyDeveloperApiCatcher.as_view(),
        name="internal_send_money_catcher",
    ),
    # urls with either jhipster or backend authentication
]
