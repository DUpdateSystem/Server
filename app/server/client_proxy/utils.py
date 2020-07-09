from multiprocessing import Manager

__manager = Manager()


def get_manager_value(key, value):
    return __manager.Value(key, value)


def get_manager_list():
    return __manager.list()


def get_manager_dict():
    return __manager.dict()


def get_key(method: str, url: str, headers: dict or None,
            body_type: str or None, body_text: str or None) -> str:
    key = f"{method}-{url}-{headers}"
    if body_type and body_text:
        key += f"-{body_type}-{body_text}"
    return key


class ProxyKilledError(Exception):
    pass
