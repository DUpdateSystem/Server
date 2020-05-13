from .server.api import get_app_status, get_download_info
from .server.utils import logging


def debug(hub_uuid: str, app_id_option):
    app_id = []
    for i in range(int(len(app_id_option) / 2)):
        app_id.append({
            "key": app_id_option[i],
            "value": app_id_option[i + 1]
        })
    logging.info(f"开始测试：hub_uuid:{hub_uuid}, app_id:{app_id}")
    logging.info("测试 get_app_status 函数")
    logging.debug(get_app_status(hub_uuid, app_id))
    logging.info("测试 get_download_info 函数")
    logging.debug(get_download_info(hub_uuid, app_id, [0, 0]))
