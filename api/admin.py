from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import App, DailyMetrics, JhiUser


# @admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("name", "public_token", "wallet", "status", "active", "date_created")
    search_fields = ("name", "public_token", "wallet", "user__login", "user__email")
    list_filter = ("status", "active", "date_created")
    raw_id_fields = ("user",)


class JhiUserAdmin(admin.ModelAdmin):
    list_display = (
        "login",
        "email",
        "first_name",
        "last_name",
        "activated",
        "email_validated",
        "created_date",
        "last_modified_date",
    )
    search_fields = ("login", "email", "first_name", "last_name")
    list_filter = ("activated", "email_validated", "created_date", "last_modified_date")
    readonly_fields = ("created_date", "last_modified_date")


class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "day",
        "transactions",
        "app",
        "amount_sum",
        "fee_sum",
        "amount_average",
        "fee_average",
        "transaction_type",
    )
    search_fields = ("day", "app__name", "transaction_type")
    list_filter = ("day", "transaction_type")


admin.site.register(Permission)

admin.site.register(App, AppAdmin)
admin.site.register(DailyMetrics, DailyMetricsAdmin)
admin.site.register(JhiUser, JhiUserAdmin)
