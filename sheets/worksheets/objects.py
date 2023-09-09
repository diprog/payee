from sheets.sheets import get_from_cache


def get(username):
    object_names = []
    for o in get_from_cache('objects'):
        try:
            if o.username == username:
                object_names.append(o.name)
        except:
            object_names.append(o)
    return object_names
