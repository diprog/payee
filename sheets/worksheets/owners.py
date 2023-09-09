from sheets.sheets import get_from_cache, User


def get(username=None, name=None) -> User | list[User] | None:
    users = get_from_cache('owners')
    for user in users:
        if (username and user.username == username) or (name and user.name == name):
            return user
    if username or name:
        return None
    return users
