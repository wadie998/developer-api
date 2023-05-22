from settings.logging.custom_gunicorn_logger import CustomGunicornLogger

"""
gunicorn --bind 0.0.0.0:8000 settings.wsgi --access-logfile - -w 4 --timeout 60
    --logger-class=utils.logging.custom_gunicorn_logger.CustomGunicornLogger
"""

bind = "0.0.0.0:8000"
workers = 4
timeout = 60
logger_class = CustomGunicornLogger
accesslog = "-"
