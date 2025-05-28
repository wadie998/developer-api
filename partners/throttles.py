# throttles.py
import hashlib
import time

from django.core.cache import cache
from rest_framework.throttling import BaseThrottle


class GenericRequestThrottle(BaseThrottle):
    """
    Generic throttle that limits identical requests based on configurable fields and merchant.
    Can be customized per view with different scopes, timeouts, and field combinations.
    """

    cache_format = "throttle_generic_%(scope)s_%(ident)s"

    # Default configuration - can be overridden in view or subclass
    scope = "default"
    timeout_seconds = 10
    merchant_field_path = "application.merchant_id"  # dot notation for nested access
    throttle_fields = []  # Fields to include in throttle key
    require_all_fields = False  # If True, all fields must be present; if False, at least one

    def get_merchant_id(self, request):
        """
        Extract merchant ID from request using configurable path.
        Supports dot notation like 'application.merchant_id' or 'user.merchant.id'
        """
        try:
            obj = request
            for attr in self.merchant_field_path.split("."):
                obj = getattr(obj, attr)
            return str(obj)
        except (AttributeError, TypeError):
            return None

    def get_request_data(self, request):
        """
        Get request data based on HTTP method.
        """
        if request.method == "GET":
            return request.GET
        else:
            return request.data

    def extract_throttle_values(self, request):
        """
        Extract values for throttle fields from request data.
        Returns a list of values in the same order as throttle_fields.
        """
        data = self.get_request_data(request)
        values = []

        for field in self.throttle_fields:
            # Support dot notation for nested fields
            if "." in field:
                value = data
                try:
                    for key in field.split("."):
                        value = value.get(key) if hasattr(value, "get") else getattr(value, key)
                except (AttributeError, KeyError, TypeError):
                    value = None
            else:
                value = data.get(field)

            values.append(str(value) if value is not None else "")

        return values

    def should_throttle(self, values):
        """
        Determine if request should be throttled based on field values.
        """
        if self.require_all_fields:
            # All fields must have values
            return all(value.strip() for value in values)
        else:
            # At least one field must have a value
            return any(value.strip() for value in values)

    def get_cache_key(self, request, view):
        """
        Generate a unique cache key based on merchant_id and configured fields.
        """
        # Get merchant ID
        merchant_id = self.get_merchant_id(request)
        if not merchant_id:
            return None

        # Get throttle field values
        field_values = self.extract_throttle_values(request)

        # Check if we should throttle based on field values
        if not self.should_throttle(field_values):
            return None

        # Create identifier parts
        identifier_parts = [merchant_id] + field_values

        # Create a hash of the identifier
        identifier_string = "|".join(identifier_parts)
        identifier_hash = hashlib.sha256(identifier_string.encode()).hexdigest()[:32]

        return self.cache_format % {"scope": self.scope, "ident": identifier_hash}

    def allow_request(self, request, view):
        """
        Implement the throttling logic.
        """
        cache_key = self.get_cache_key(request, view)

        # If we can't generate a cache key, allow the request
        if cache_key is None:
            return True

        # Check if this exact request was made recently
        last_request_time = cache.get(cache_key)
        now = time.time()

        if last_request_time is None:
            # First request with this combination
            cache.set(cache_key, now, timeout=self.timeout_seconds)
            return True

        # Check if enough time has passed since last request
        time_since_last = now - last_request_time

        if time_since_last >= self.timeout_seconds:
            # Enough time has passed, allow request
            cache.set(cache_key, now, timeout=self.timeout_seconds)
            return True
        else:
            # Not enough time, throttle the request
            return False

    def wait(self):
        """
        Return the number of seconds to wait before the next request is allowed.
        """
        return self.timeout_seconds


class TransactionStatusThrottle(GenericRequestThrottle):
    """
    Throttle for transaction status requests.
    """

    scope = "transaction_status"
    timeout_seconds = 8
    throttle_fields = ["developer_tracking_id", "flouci_transaction_id"]
    require_all_fields = False  # At least one transaction ID required
