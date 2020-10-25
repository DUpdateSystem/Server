import json

from gpapi.googleplay import GooglePlayAPI as _GooglePlayAPI

from app.server.manager.data.constant import logging
from app.server.manager.data.generator_cache import GeneratorCache
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, return_value_no_break, get_tmp_cache, add_tmp_cache

_locale = "zh_CN"
_timezone = "UTC"
_device_codename = "walleye"

_auth_cache_key = "google_play_def_token"


class GooglePlay(BaseHub):
    def init_account(self, account: dict) -> dict or None:
        mail = account['mail']
        passwd = account['passwd']
        api = self.__init_google_play_by_account(mail, passwd)
        return {
            "gsfId": api.gsfId,
            "authSubToken": api.authSubToken
        }

    async def get_release_list(self, generator_cache: GeneratorCache,
                               app_id_list: list, auth: dict or None = None):
        [return_value_no_break(generator_cache, app_id, []) for app_id in app_id_list if
         android_app_key not in app_id]
        package_list = [app_id[android_app_key] for app_id in app_id_list if android_app_key in app_id]
        # noinspection PyBroadException
        try:
            api = self.__get_google_api(auth)
            bulk_details = api.bulkDetails(package_list)
        except Exception:
            api = self.__get_def_google_play()
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
        # noinspection PyBroadException
        try:
            api = self.__get_google_api(auth)
            download = api.download(doc_id, expansion_files=True)
        except Exception:
            api = self.__get_def_google_play()
            download = api.download(doc_id, expansion_files=True)
        main_apk_file = download['file']
        download_list.append({"name": f'{doc_id}.apk',
                              "url": main_apk_file['url'],
                              "headers": main_apk_file['headers'],
                              "cookies": main_apk_file['cookies']})
        splits_apk_file = download['splits']
        for apk in splits_apk_file:
            apk_file = apk['file']
            download_list.append({"name": f"{apk['name']}.apk",
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

    def __get_google_api(self, auth: dict):
        if auth:
            gsf_id, auth_sub_token = self.__get_auth(auth)
        else:
            auth = self.__get_cache_auth()
            if auth:
                gsf_id, auth_sub_token = auth
            else:
                return self.__get_def_google_play()
        return self.__init_google_play_by_token(gsf_id, auth_sub_token)

    def __get_def_google_play(self) -> _GooglePlayAPI:
        api = self.__init_google_play_by_account("xiangzhedev@gmail.com", "slzlpcugmdydxvii")
        add_tmp_cache(_auth_cache_key, json.dumps({"gsfId": api.gsfId, "authSubToken": api.authSubToken}))
        return api

    @staticmethod
    def __init_google_play_by_account(mail: str, passwd: str) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        api.login(mail, passwd)
        return api

    @staticmethod
    def __init_google_play_by_token(gsf_id: int, auth_sub_token: str) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        logging.info("GooglePlay: Renew Auth")
        return api

    def __get_cache_auth(self) -> tuple or None:
        auth = get_tmp_cache(_auth_cache_key)
        if auth:
            return self.__get_auth(auth)
        else:
            return None

    @staticmethod
    def __get_auth(auth: dict):
        return int(auth["gsfId"]), auth["authSubToken"]


class GooglePlayAPI(_GooglePlayAPI):
    def _deliver_data(self, url, cookies):
        headers = self.getHeaders()
        return {
            "url": url,
            "headers": headers,
            "cookies": cookies
        }
