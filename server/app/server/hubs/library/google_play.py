import json
from gpapi.googleplay import GooglePlayAPI as _GooglePlayAPI, RequestError

from app.server.manager.data.generator_cache import GeneratorCache
from ..base_hub import BaseHub
from app.server.manager.data.constant import logging
from ..hub_script_utils import android_app_key, return_value_no_break, get_tmp_cache, add_tmp_cache

_locale = "zh_CN"
_timezone = "UTC"
_device_codename = "walleye"

_auth_cache_key = "google_play_def_token"


class GooglePlay(BaseHub):
    def init_account(self, account: dict) -> dict or None:
        mail = account['mail']
        passwd = account['passwd']
        api = _GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        api.login(email=mail, password=passwd)
        return {
            "gsfId": api.gsfId,
            "authSubToken": api.authSubToken
        }

    async def get_release_list(self, generator_cache: GeneratorCache,
                               app_id_list: list, auth: dict or None = None):
        api = _GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        gsf_id, auth_sub_token = self.__get_auth(auth)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        [return_value_no_break(generator_cache, app_id, []) for app_id in app_id_list if android_app_key not in app_id]
        package_list = [app_id[android_app_key] for app_id in app_id_list if android_app_key in app_id]
        try:
            bulk_details = api.bulkDetails(package_list)
        except RequestError:
            gsf_id, auth_sub_token = self.__get_new_token()
            api.gsfId = gsf_id
            api.setAuthSubToken(auth_sub_token)
            bulk_details = api.bulkDetails(package_list)
        for i, l_details in enumerate(bulk_details):
            app_id = app_id_list[i]
            if l_details is None:
                return_value_no_break(generator_cache, app_id, [])
            else:
                # noinspection PyBroadException
                try:
                    package = package_list[i]
                    details = api.details(package)['details']['appDetails']
                    release = {
                        'version_number': details['versionString'],
                        'assets': [{
                            'file_name': package + '.apk'
                        }]
                    }
                    if 'recentChangesHtml' in details:
                        release['change_log'] = details['recentChangesHtml']
                    release_list = [release, ]
                except Exception:
                    release_list = None
                return_value_no_break(generator_cache, app_id, release_list)

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> tuple or None:
        if android_app_key not in app_id:
            return None
        download_list = []
        doc_id = app_id[android_app_key]
        api = GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        gsf_id, auth_sub_token = self.__get_auth(auth)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        download = api.download(doc_id, expansion_files=True)
        apk_file = download['file']
        download_list.append({"name": f'{doc_id}.apk',
                              "url": apk_file['url'],
                              "headers": apk_file['headers'],
                              "cookies": apk_file['cookies']})
        for obb in download['additionalData']:
            obb_file = obb['file']
            obb_file_name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
            download_list.append({"name": obb_file_name,
                                  "url": obb_file['url'],
                                  "headers": obb_file['headers'],
                                  "cookies": obb_file['cookies']})
        return download_list

    def __get_auth(self, auth: dict):
        if 'gsfId' not in auth or 'authSubToken' not in auth:
            auth = self.__get_def_auth()
        return int(auth["gsfId"]), auth["authSubToken"]

    def __get_def_auth(self):
        auth = get_tmp_cache(_auth_cache_key)
        if not auth:
            return self.__get_new_token()
        else:
            auth_json = json.loads(auth)
            if not self.__check_health_limit_num(auth_json):
                if self.__check_token(auth_json):
                    self.__set_auth_limit_num(auth_json, 25)
                    return auth_json
                else:
                    return self.__get_new_token()
            self.__set_auth_limit_num(auth_json)
            return auth_json

    def __check_health_limit_num(self, auth: dict):
        return self.__have_health_limit_num(auth) and int(auth["health_limit_num"]) > 0

    @staticmethod
    def __have_health_limit_num(auth: dict):
        try:
            int(auth["health_limit_num"])
            return True
        except KeyError:
            return False
        except TypeError:
            return False

    def __set_auth_limit_num(self, auth: dict, limit_num: int or None = None):
        if limit_num is None and self.__have_health_limit_num(auth):
            limit_num = int(auth["health_limit_num"]) - 1
        auth["health_limit_num"] = limit_num
        add_tmp_cache(_auth_cache_key, json.dumps(auth))

    def __check_token(self, auth: dict) -> bool:
        logging.info("GooglePlay: Check Token")
        api = _GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        gsf_id, auth_sub_token = self.__get_auth(auth)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        test_details = api.details("com.google.android.webview")
        try:
            test_details = api.details("com.google.android.webview")
        except RequestError:
            pass
        if test_details:
            return True
        else:
            return False

    def __get_new_token(self) -> dict:
        auth_json = self.init_account({
            "mail": "xiangzhedev@gmail.com",
            "passwd": "slzlpcugmdydxvii",
        })
        self.__set_auth_limit_num(auth_json, 25)
        logging.info("GooglePlay: Renew Token")
        return auth_json


class GooglePlayAPI(_GooglePlayAPI):
    def _deliver_data(self, url, cookies):
        headers = self.getHeaders()
        return {
            "url": url,
            "headers": headers,
            "cookies": cookies
        }
