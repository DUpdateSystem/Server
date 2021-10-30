import json

from quart import request


def path_to_dict(path: str) -> dict[str, str]:
    spite_list = path.split('/')
    return dict(zip(spite_list[::2], spite_list[1::2]))


def get_auth() -> dict or None:
    raw_auth = request.headers.get("Authorization")
    if raw_auth:
        auth = json.loads(raw_auth)
    else:
        auth = None
    return auth


def path_to_int_list(path: str) -> list[int]:
    return [int(i) for i in path.split('/')]
