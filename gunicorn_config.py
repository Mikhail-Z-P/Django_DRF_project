import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", 3))
timeout = 120
loglevel = "info"
accesslog = "-"
errorlog = "-"
