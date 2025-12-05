from django.core.cache import cache


def set_user_status(user_id: int, is_online: bool):
    if user_id is None:
        return
    if is_online:
        cache.set(f"user_{user_id}_online", True)
    else:
        cache.delete(f"user_{user_id}_online")


def is_user_online(user_id: int) -> bool:
    if user_id is None:
        return False
    return cache.get(f"user_{user_id}_online", False) is True
