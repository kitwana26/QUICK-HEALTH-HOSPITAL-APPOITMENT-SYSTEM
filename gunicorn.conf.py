import multiprocessing
import os
import sys
from pathlib import Path


# Get the project root and BACKEND directories
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / 'BACKEND'

# Add both to Python path - must add BACKEND first so Django is found
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(root_dir))

# Change to BACKEND directory where Django project is located
os.chdir(backend_dir)

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(
    os.getenv(
        "GUNICORN_WORKERS",
        str((multiprocessing.cpu_count() * 2) + 1),
    )
)
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
wsgi_app = "hospital_project.wsgi:application"
