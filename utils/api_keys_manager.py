from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey


class ApiKeyServicesNames:
    SERVICE1 = "SERVICE1"
    SERVICE2 = "SERVICE2"
    BACKEND = "BACKEND"


class HasCustomApiKey(HasAPIKey):
    name = None
    name_starts_with = None

    def get_api_key_name(self, request):
        api_key = APIKey.objects.get(prefix=self.get_key(request).partition(".")[0])
        request.api_key = api_key
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


# To add a new service api keys permission class:
# Add a class that inherits from HasCustomApiKey
# your class must override the attribute 'name' or 'name_starts_with' with any string representing the service name


class HasService1ApiKey(HasCustomApiKey):
    name = ApiKeyServicesNames.SERVICE1


class HasService2ApiKey(HasCustomApiKey):
    name_starts_with = ApiKeyServicesNames.SERVICE2


class HasBackendApiKey(HasCustomApiKey):
    name = ApiKeyServicesNames.BACKEND
    name_starts_with = ApiKeyServicesNames.BACKEND
