import json

import requests
from gpapi.googleplay import GooglePlayAPI as _GooglePlayAPI, \
    PURCHASE_URL, ssl_verify, googleplay_pb2, LoginError, RequestError

from app.server.manager.data.constant import logging
from app.server.manager.data.generator_cache import GeneratorCache
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, return_value_no_break, get_tmp_cache, add_tmp_cache

_locale = "zh_CN"
_timezone = "UTC"
_device_codename = "walleye"

_auth_cache_key = "google_play_def_token"


class GooglePlay(BaseHub):
    @staticmethod
    def get_uuid() -> str:
        return '65c2f60c-7d08-48b8-b4ba-ac6ee924f6fa'

    def init_account(self, account: dict) -> dict or None:
        mail = account['mail']
        passwd = account['passwd']
        api = self.__init_google_play_by_account(mail, passwd)
        return {
            "gsfId": api.gsfId,
            "ac2dmToken": api.authSubToken
        }

    async def get_release_list(self, generator_cache: GeneratorCache,
                               app_id_list: list, auth: dict or None = None):
        [return_value_no_break(generator_cache, app_id, []) for app_id in app_id_list if
         android_app_key not in app_id]
        package_list = ["com.google.android.webview"] + [app_id[android_app_key] for app_id in app_id_list if
                                                         android_app_key in app_id]
        package_list = set(package_list)
        package_list = list(package_list)
        # noinspection PyBroadException
        try:
            api = self.__get_google_api(auth)
            bulk_details = api.bulkDetails(package_list)
        except Exception:
            api = self.__get_def_google_play()
            bulk_details = api.bulkDetails(package_list)
        details_map = {}
        for i, l_details in enumerate(bulk_details):
            package = package_list[i]
            details_map[package] = l_details
        if details_map["com.google.android.webview"] is None:
            api = self.__get_def_google_play()
            bulk_details = api.bulkDetails(package_list)
            for i, l_details in enumerate(bulk_details):
                package = package_list[i]
                details_map[package] = l_details
        for package, details in details_map.items():
            app_id = {android_app_key: package}
            if details is None:
                return_value_no_break(generator_cache, app_id, [])
            else:
                # noinspection PyBroadException
                try:
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
            # noinspection PyBroadException
            try:
                api = self.__get_def_google_play()
                download = api.download(doc_id, expansion_files=True)
            except Exception:
                api = self.__get_def_google_play(use_spare=True)
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
        return self.__init_google_play_by_gsfid_and_token(auth_sub_token, gsf_id)

    def __get_def_google_play(self, use_spare=False) -> _GooglePlayAPI:
        if use_spare:
            logging.warn("GooglePlay: Use Spare Aurora API")
            email, token = _get_aurora_token(1)
        else:
            email, token = _get_aurora_token(0)
        api = self.__init_google_play_by_email_and_token(email, token)
        add_tmp_cache(_auth_cache_key, json.dumps({"gsfId": api.gsfId, "ac2dmToken": api.authSubToken}))
        logging.info("GooglePlay: Renew Auth")
        return api

    @staticmethod
    def __init_google_play_by_account(mail: str, passwd: str) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        api.login(mail, passwd)
        return api

    @staticmethod
    def __init_google_play_by_gsfid_and_token(auth_sub_token: str, gsf_id: int) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        return api

    @staticmethod
    def __init_google_play_by_email_and_token(email: str, ac2dm_token: str) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale, timezone=_timezone, device_codename=_device_codename)
        api.gsfId = api.checkin(email, ac2dm_token)
        api.setAuthSubToken(ac2dm_token)
        api.uploadDeviceConfig()
        return api

    def __get_cache_auth(self) -> tuple or None:
        auth = get_tmp_cache(_auth_cache_key)
        if auth:
            auth_json = json.loads(auth)
            return self.__get_auth(auth_json)
        else:
            return None

    @staticmethod
    def __get_auth(auth: dict):
        return int(auth["gsfId"]), auth["ac2dmToken"]


# 使用了 Aurora 公共帐号接口，感谢 AuroraStore 项目及其开发者 whyorean
_aurora_token_api_url_list = ("http://auroraoss.com:8080", "http://auroraoss.in:8080")


def _get_aurora_token(index: int) -> tuple:
    aurora_token_api_url = _aurora_token_api_url_list[index]
    email = requests.get(f"{aurora_token_api_url}/email").text
    token = requests.get(f"{aurora_token_api_url}/token/email/{email}").text
    return email, token


class GooglePlayAPI(_GooglePlayAPI):

    def getHeaders(self, upload_fields=False):
        """Return the default set of request headers, which
        can later be expanded, based on the request type"""

        if upload_fields:
            headers = self.deviceBuilder.getDeviceUploadHeaders()
        else:
            headers = self.deviceBuilder.getBaseHeaders()
        if self.gsfId is not None:
            headers["X-DFE-Device-Id"] = "{0:x}".format(self.gsfId)
        if self.authSubToken is not None:
            headers["Authorization"] = f"Bearer {self.authSubToken}"
            # 依据 com.dragons.aurora.playstoreapiv2 的 GooglePlayAPI 类  getDefaultHeaders 函数 832 行修改
            # 感谢 playstoreapiv2 项目及其开发者们
        if self.device_config_token is not None:
            headers["X-DFE-Device-Config-Token"] = self.device_config_token
        if self.deviceCheckinConsistencyToken is not None:
            headers["X-DFE-Device-Checkin-Consistency-Token"] = self.deviceCheckinConsistencyToken
        if self.dfeCookie is not None:
            headers["X-DFE-Cookie"] = self.dfeCookie
        return headers

    # noinspection PyPep8Naming
    def download(self, packageName, versionCode=None, offerType=1, expansion_files=False):
        """
        避免 Unexpected end-group tag. 错误
        参考：https://github.com/NoMore201/googleplay-api/issues/132
        """

        if self.authSubToken is None:
            raise LoginError("You need to login before executing any request")

        if versionCode is None:
            # pick up latest version
            appDetails = self.details(packageName).get('details').get('appDetails')
            versionCode = appDetails.get('versionCode')

        headers = self.getHeaders()
        params = {'ot': str(offerType),
                  'doc': packageName,
                  'vc': str(versionCode)}
        response = requests.post(PURCHASE_URL, headers=headers,
                                 params=params, verify=ssl_verify,
                                 timeout=60,
                                 proxies=self.proxies_config)

        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)
        else:
            dlToken = response.payload.buyResponse.downloadToken
            return self.delivery(packageName, versionCode, offerType, dlToken,
                                 expansion_files=expansion_files)

    def _deliver_data(self, url, cookies):
        headers = self.getHeaders()
        return {
            "url": url,
            "headers": headers,
            "cookies": cookies
        }
