from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey


class ApiKeyServicesNames:
    BACKEND = "BACKEND"


class HasCustomApiKey(HasAPIKey):
    name = None
    name_starts_with = None

    def get_api_key_name(self, request):
        api_key = APIKey.objects.get(prefix=self.get_key(request).partition(".")[0])
        request.api_key = api_key
        request.tracking_id = None
        return api_key.name

    def check_api_key_name(self, request):
        if self.name_starts_with:
            return self.get_api_key_name(request).startswith(self.name_starts_with)
        elif self.name:
            return self.get_api_key_name(request) == self.name
        else:
            return True

    def has_permission(self, request, view):
        return super(HasAPIKey, self).has_permission(request, view) and self.check_api_key_name(request)


class HasBackendApiKey(HasCustomApiKey):
    name = ApiKeyServicesNames.BACKEND
