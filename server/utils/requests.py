import requests
from requests import Response

session = requests.Session()


def get_response(url: str, throw_error=False, **kwargs) -> Response or None:
    try:
        response = session.get(url, **kwargs, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        if throw_error:
            raise e
        return None
