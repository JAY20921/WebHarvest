"""
Celery Application Configuration
"""

import ssl
import sys
from celery import Celery
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'intelligent_scraper',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.workers.extraction_worker']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    broker_connection_retry_on_startup=True,
    # Cloud Redis (Upstash etc.) closes idle connections; keep them healthy
    broker_transport_options={'health_check_interval': 30},
    result_backend_transport_options={'health_check_interval': 30},
    redis_backend_health_check_interval=30,
)

# Cloud Redis providers (Upstash, Redis Cloud) require TLS via rediss://.
# Celery refuses rediss:// URLs unless SSL options are configured explicitly.
_ssl_options = {'ssl_cert_reqs': ssl.CERT_REQUIRED}
if settings.CELERY_BROKER_URL.startswith('rediss://'):
    celery_app.conf.broker_use_ssl = _ssl_options
if settings.CELERY_RESULT_BACKEND.startswith('rediss://'):
    celery_app.conf.redis_backend_use_ssl = _ssl_options

# The default prefork pool does not work on Windows
if sys.platform == 'win32':
    celery_app.conf.worker_pool = 'solo'

logger.info("Celery app configured")
