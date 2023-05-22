import logging

from gunicorn import glogging


class CustomGunicornLogger(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)

        # Add filters to Gunicorn logger
        logger = logging.getLogger("gunicorn.access")
        # logger.addFilter(StaticFilesFilter())
        logger.addFilter(HealthCheckFilter())

'''
# Uncomment to disable /static logs
class StaticFilesFilter(logging.Filter):
    def filter(self, record):
        return "GET /static" not in record.getMessage()
'''

class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return "/api/ht" not in record.getMessage()
