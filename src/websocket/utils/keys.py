def user_group_name(user_id: int) -> str:
    return f"user_{user_id}"


def user_online_status_key(user_id: int) -> str:
    return f"user_{user_id}_online"
