from redis_connection import redis_conn


SESSION_EXPIRATION = 86400


def set_session(user_id, key, value):
    session_key = f"user_session:{user_id}:{key}"
    redis_conn.set(session_key, value, ex=SESSION_EXPIRATION)


def get_session(user_id, key):
    session_key = f"user_session:{user_id}:{key}"
    return redis_conn.get(session_key)


def delete_session(user_id, key):
    session_key = f"user_session:{user_id}:{key}"
    redis_conn.delete(session_key)
