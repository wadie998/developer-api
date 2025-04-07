from django.contrib.sites.models import Site


def generate_absolute_uri(path, https=False):
    """Turn a relative URL into an absolute URL."""

    site = Site.objects.get_current()
    protocol = "https" if https else "http"
    return f"{protocol}://{site.domain}{path}"
