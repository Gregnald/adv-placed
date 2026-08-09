import json
import redis

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True,
        socket_timeout=2
    )
    redis_client.ping()
    redis_available = True
except Exception as e:
    redis_client = None
    redis_available = False


def save_session_redis(session_id, user_id, user_role, ttl_seconds=86400):
    if not redis_available or not redis_client or not session_id:
        return False
    try:
        data = json.dumps({'user_id': user_id, 'user_type': user_role})
        redis_client.set(f"session:{session_id}", data, ex=ttl_seconds)
        return True
    except Exception:
        return False


def get_session_redis(session_id):
    if not redis_available or not redis_client or not session_id:
        return None
    try:
        raw_data = redis_client.get(f"session:{session_id}")
        if raw_data:
            return json.loads(raw_data)
    except Exception:
        return None
    return None


def delete_session_redis(session_id):
    if not redis_available or not redis_client or not session_id:
        return False
    try:
        redis_client.delete(f"session:{session_id}")
        return True
    except Exception:
        return False
