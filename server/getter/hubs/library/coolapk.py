import base64
import hashlib
import time

from requests import request, HTTPError

from utils.logging import logging
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, get_session, get_url_from_release_fun

__session = get_session()


class CoolApk(BaseHub):
    @staticmethod
    def get_uuid() -> str:
        return '1c010cc9-cff8-4461-8993-a86cd190d377'

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        package = app_id[android_app_key]
        if package == 'android':
            return []
        url = _mk_detail_url(package)
        request_json = _request(url).json()
        # print(request_json)  # 数据测试代码
        if 'status' in request_json and request_json['status'] < 0:
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
                "download_url": _get_redirect_download_url(_mk_download_url(aid, package)),
            }]
        })

        url = _mk_history_url(aid)
        request_json = _request(url).json()
        if 'status' in request_json and request_json['status'] < 0:
            return data
        h_list = request_json['data']
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

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> dict or tuple or None:
        hub_uuid = self.get_uuid()
        download_url = get_url_from_release_fun(hub_uuid, app_id, asset_index, use_cache=True)
        try:
            r = _redirect(download_url, None)
            if 'Content-Type' not in r.headers \
                    or (r.headers['Content-Type'].split(";")[0] != 'application/vnd.android.package-archive'):
                logging.debug("返回非安装包数据")
                raise HTTPError
            logging.debug("网址验证正确")
        except HTTPError:
            logging.debug("网址错误，尝试重新获取")
            download_url = get_url_from_release_fun(hub_uuid, app_id, asset_index, use_cache=False)
        return download_url

    def available_test_url(self) -> str:
        return "https://api.coolapk.com/"


def _mk_detail_url(app_package: str) -> str:
    return f"https://api.coolapk.com/v6/apk/detail?id={app_package}"


def _mk_history_url(app_id: str) -> str:
    return f"https://api.coolapk.com/v6/apk/downloadVersionList?id={app_id}"


def _mk_download_url(aid: str, app_package: str) -> str:
    return f"https://api.coolapk.com/v6/apk/download?pn={app_package}&aid={aid}"


def _get_history_download_url(aid: str, app_package: str, version_id: str) -> str:
    row_url = f"https://api.coolapk.com/v6/apk/downloadHistory?pn={app_package}&aid={aid}&versionId={version_id}&downloadFrom=coolapk"
    return _get_redirect_download_url(row_url)


def _get_redirect_download_url(url):
    r = _redirect(url, __mk_headers())
    return _redirect(r.url, None).url


def _redirect(url, headers) -> request:
    r = __session.head(url, headers=headers, allow_redirects=True, timeout=15)
    return r


# 加密算法来自 https://github.com/ZCKun/CoolapkTokenCrack、https://zhuanlan.zhihu.com/p/69195418
__DEVICE_ID = "55077056-48ee-46c8-80a6-2a21a9c5b12b"


def _request(url: str):
    headers = __mk_headers()
    return __session.get(url, headers=headers, timeout=15)


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
