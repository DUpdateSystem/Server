def get_key(method: str, url: str, headers: dict or None,
            body_type: str or None, body_text: str or None) -> str:
    key = f"{method}-{url}-{headers}"
    if body_type and body_text:
        key += f"-{body_type}-{body_text}"
    return key


class ProxyKilledError(Exception):
    def __init__(self, index):
        self.client_index = index
