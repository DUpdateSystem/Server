import os
import time
import pathlib
from datetime import timedelta
from app.server.config import server_config as _server_config
from app.server.utils import time_loop

_asset_dir_path = _server_config.download_asset_dir_path
_asset_dir_path.mkdir(parents=True, exist_ok=True)


def __mk_url(file_name: str) -> str:
    return f'http://{_server_config.download_asset_host}/download/{file_name}'


def write_byte_asset(file_name: str, byte_list):
    file_path = _asset_dir_path.joinpath(file_name)
    with open(file_path, "wb") as f:
        if byte_list is bytes:
            f.write(byte_list)
        else:
            for chunk in byte_list:
                f.write(chunk)
    return __mk_url(file_name)


def read_byte_asset(file_name: str) -> bytes:
    file_path = _asset_dir_path.joinpath(file_name)
    with open(file_path, "rb") as f:
        return f.read()


@time_loop.job(interval=timedelta(hours=_server_config.auto_refresh_time))
def __auto_clean_old_file():
    for (dir_path, _, filenames) in os.walk(_asset_dir_path):
        file = pathlib.PurePath(dir_path, filenames)
        ctime = os.path.getctime(file)
        current = time.time()
        if current - ctime >= 24 * 3600:
            os.remove(file)
