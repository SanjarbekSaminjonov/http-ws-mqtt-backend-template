from django.core.cache import cache

from websocket.utils.keys import user_online_status_key


def set_user_status(user_id: int, is_online: bool):
    if user_id is None:
        return
    if is_online:
        cache.set(user_online_status_key(user_id), True)
    else:
        cache.delete(user_online_status_key(user_id))


def is_user_online(user_id: int) -> bool:
    if user_id is None:
        return False
    return bool(cache.get(user_online_status_key(user_id), False))
