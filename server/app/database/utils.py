from json import loads, dumps


def from_json(value) -> str or None:
    if value:
        return loads(str(value))
    else:
        return None


def to_json(value) -> str or None:
    if value:
        return dumps(value, sort_keys=True)
    else:
        return None
