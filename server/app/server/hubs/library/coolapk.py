import base64
import hashlib
import time

import requests

from app.server.manager.data.constant import logging
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, get_session


class CoolApk(BaseHub):
    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        package = app_id[android_app_key]
        if package == 'android':
            return []
        url = _get_detail_url(package)
        request_json = _request(url).json()
        if 'message' in request_json and request_json['message'] == '应用不存在':
            return []
        data = []
        detail = request_json['data']
        aid = detail['id']
        newest_version_number = detail['apkversionname']
        data.append({
            "version_number": newest_version_number,
            "change_log": detail['changelog'],
            "assets": [{
                "file_name": f"{package}-{newest_version_number}.apk",
                "download_url": _get_redirect_url(_get_download_url(aid, package)),
            }]
        })

        url = _get_history_url(aid)
        h_list = _request(url).json()['data']
        for h in h_list:
            version_number = h['versionName']
            version_id = h['versionId']
            data.append({
                "version_number": version_number,
                "assets": [{
                    "file_name": f"{package}-{version_number}.apk",
                    "download_url": _get_history_download_url(aid, package, version_id),
                }]
            })
        return data

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> tuple or None:
        from app.server.hubs.hub_list import hub_dict
        hub_uuid = None
        for uuid in hub_dict:
            if self is hub_dict[uuid]:
                hub_uuid = uuid
                break
        download_url = _re_get_download_url(hub_uuid, app_id, asset_index, True)
        try:
            r = get_session().head(download_url)
            content_type = r.headers['Content-Type'].split(";")[0]
            if content_type != 'application/vnd.android.package-archive':
                logging.debug("返回非安装包数据")
                raise requests.HTTPError
            logging.debug("网址验证正确")
        except requests.HTTPError:
            logging.debug("网址错误，尝试重新获取")
            download_url = _re_get_download_url(hub_uuid, app_id, asset_index, False)
        return (download_url,),


def _re_get_download_url(hub_uuid, app_id, asset_index, use_cache):
    from app.server.manager.data_manager import data_manager
    release_list = next(data_manager.get_release(hub_uuid, [app_id], use_cache=use_cache))["release_list"]
    return release_list[asset_index[0]]["assets"][asset_index[1]]["download_url"]


def _get_detail_url(app_package: str) -> str:
    return f"https://api.coolapk.com/v6/apk/detail?id={app_package}"


def _get_history_url(app_id: str) -> str:
    return f"https://api.coolapk.com/v6/apk/downloadVersionList?id={app_id}"


def _get_download_url(aid: str, app_package: str) -> str:
    return f"https://api.coolapk.com/v6/apk/download?pn={app_package}&aid={aid}"


def _get_history_download_url(aid: str, app_package: str, version_id: str) -> str:
    row_url = f"https://api.coolapk.com/v6/apk/downloadHistory?pn={app_package}&aid={aid}&versionId={version_id}&downloadFrom=coolapk"
    return _get_redirect_url(row_url)


def _get_redirect_url(url):
    headers = __mk_headers()
    r = requests.head(url, headers=headers, allow_redirects=True)
    return r.url


# 加密算法来自 https://github.com/ZCKun/CoolapkTokenCrack、https://zhuanlan.zhihu.com/p/69195418
__DEVICE_ID = "8513efac-09ea-3709-b214-95b366f1a185"


def _request(url: str):
    headers = __mk_headers()
    return requests.get(url, headers=headers)


def __get_app_token() -> str:
    t = int(time.time())
    hex_t = hex(t)

    # 时间戳加密
    md5_t = hashlib.md5(str(t).encode('utf-8')).hexdigest()

    # 不知道什么鬼字符串拼接
    a = f'token://com.coolapk.market/c67ef5943784d09750dcfbb31020f0ab?{md5_t}${__DEVICE_ID}&com.coolapk.market'

    # 不知道什么鬼字符串拼接 后的字符串再次加密
    md5_a = hashlib.md5(base64.b64encode(a.encode('utf-8'))).hexdigest()

    token = f'{md5_a}{__DEVICE_ID}{hex_t}'
    return token


def __mk_headers() -> dict:
    return {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; MI 8 SE MIUI/9.5.9) (#Build; Xiaomi; MI 8 SE; PKQ1.181121.001; 9) +CoolMarket/9.2.2-1905301",
        "X-App-Id": "com.coolapk.market",
        "X-Requested-With": "XMLHttpRequest",
        "X-Sdk-Int": "28",
        "X-Sdk-Locale": "zh-CN",
        "X-Api-Version": "9",
        "X-App-Version": "9.2.2",
        "X-App-Code": "1903501",
        "X-App-Device": "QRTBCOgkUTgsTat9WYphFI7kWbvFWaYByO1YjOCdjOxAjOxEkOFJjODlDI7ATNxMjM5MTOxcjMwAjN0AyOxEjNwgDNxITM2kDMzcTOgsTZzkTZlJ2MwUDNhJ2MyYzM",
        "Host": "api.coolapk.com",
        "X-Dark-Mode": "0",
        "X-App-Token": __get_app_token(),
    }
