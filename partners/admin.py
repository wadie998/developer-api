from django.contrib import admin

from .models import LinkedAccount, PartnerTransaction


class LinkedAccountAdmin(admin.ModelAdmin):
    list_display = (
        "time_created",
        "app",
        "phone_number",
        "partner_tracking_id",
        "account_tracking_id",
        "merchant_id",
        "time_modified",
    )
    search_fields = ("partner_tracking_id", "account_tracking_id", "merchant_id", "phone_number")
    readonly_fields = ("time_created", "time_modified")
    raw_id_fields = ("app",)
    ordering = ("-time_created",)


class PartnerTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "operation_id",
        "operation_type",
        "sender",
        "receiver",
        "amount_in_millimes",
        "operation_status",
        "blockchain_ref",
        "time_created",
        "time_modified",
    )
    raw_id_fields = ["sender", "receiver"]
    search_fields = ("operation_id", "operation_type", "blockchain_ref")
    list_filter = ("operation_type", "operation_status", "time_created", "time_modified")
    readonly_fields = ("time_created", "time_modified")
    ordering = ("-time_created",)


admin.site.register(LinkedAccount, LinkedAccountAdmin)
admin.site.register(PartnerTransaction, PartnerTransactionAdmin)
