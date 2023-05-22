import logging
import logging.config  # needed when logging_config doesn't start with logging.config

from django.views.debug import ExceptionReporter
from django.utils.log import AdminEmailHandler
from pathlib import Path


request_logger = logging.getLogger("django.request")



class CustomExceptionReporter(ExceptionReporter):
    """Organize and coordinate reporting on exceptions."""

    @property
    def html_template_path(self):
        return Path(__file__).parent /  "technical_500.html"

    @property
    def text_template_path(self):
        return Path(__file__).parent /  "technical_500.txt"



class CustomAdminEmailHandler(AdminEmailHandler):
    """An exception log handler that emails log entries to site admins.

    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.
    """

    def __init__(self, include_html=False, email_backend=None, reporter_class=None):
        super().__init__()
        self.include_html = include_html
        self.email_backend = email_backend
        self.reporter_class = CustomExceptionReporter
