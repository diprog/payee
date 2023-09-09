from sheets.sheets import get_from_cache, User


def get(username=None) -> User | list[User]:
    users = get_from_cache('users')
    for user in users:
        if user.username == username:
            return user
    return None if username else users
