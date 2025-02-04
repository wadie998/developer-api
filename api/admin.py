from django.contrib import admin
from django.contrib.admin import display
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission

from .models import FlouciApp, Peer


# @admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("name", "public_token", "wallet", "status", "active", "date_created")
    search_fields = ("name", "public_token", "wallet", "user__tracking_id", "user__email", "user__phone_number")
    list_filter = ("status", "active", "date_created")
    raw_id_fields = ("user",)


class JhiUserAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_id",
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "activated",
        "created_date",
        "last_modified_date",
    )
    search_fields = ("tracking_id", "email", "first_name", "last_name", "phone_number")
    list_filter = ("activated", "created_date", "last_modified_date")
    readonly_fields = ("created_date", "last_modified_date")


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = "action_time"
    list_filter = ["content_type", "action_flag"]
    search_fields = ["object_repr", "change_message", "user__username"]
    list_display = ["action_time", "user", "content_type", "action_flag", "description"]

    @display(description="description")
    def description(self, action):
        return str(action)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(Permission)
admin.site.site_header = "Django Developer Api"
admin.site.register(LogEntry, LogEntryAdmin)

admin.site.register(FlouciApp, AppAdmin)
admin.site.register(Peer, JhiUserAdmin)
