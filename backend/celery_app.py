import os
import socket
from celery import Celery


def is_redis_available(host='localhost', port=6379, timeout=0.5):
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False


def make_celery(app_name='adv_placed'):
    redis_online = is_redis_available()
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0' if redis_online else 'memory://')
    backend_url = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0' if redis_online else 'cache+memory://')

    celery = Celery(
        app_name,
        broker=broker_url,
        backend=backend_url
    )

    celery.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        task_track_started=True,
        result_expires=3600,
        task_always_eager=not redis_online,
        task_eager_propagates=True
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            from main import app
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = make_celery()
