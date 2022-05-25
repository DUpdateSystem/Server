import json
from random import randrange

import requests
from google_play_scraper import app, exceptions
from gpapi.googleplay import PURCHASE_URL
from gpapi.googleplay import GooglePlayAPI as _GooglePlayAPI
from gpapi.googleplay import (LoginError, RequestError, googleplay_pb2,
                              ssl_verify)

from utils.logging import logging

from ..base_hub import BaseHub
from ..hub_script_utils import add_tmp_cache, android_app_key, get_tmp_cache

_locale = "en_US"
_timezone = "UTC"
_device_codename = "walleye"

_auth_cache_key = "google_play_def_token"

_test_package = "com.google.android.webview"


class GooglePlay(BaseHub):

    @staticmethod
    def get_uuid() -> str:
        return '65c2f60c-7d08-48b8-b4ba-ac6ee924f6fa'

    def init_account(self, account: dict) -> dict or None:
        mail = account['mail']
        passwd = account['passwd']
        api = self.__init_google_play_by_account(mail, passwd)
        return {"gsfId": api.gsfId, "ac2dmToken": api.authSubToken}

    def get_release(self,
                    app_id: dict,
                    auth: dict or None = None) -> list or None:
        package = app_id[android_app_key]
        lang = 'zh_CN'
        country = 'us'
        try:
            result = app(package, lang=lang, country=country)
            # print(result)
        except exceptions.NotFoundError:
            return []
        release = {
            'version_number': result['version'],
            'assets': [{
                'file_name': package + '.apk'
            }]
        }
        try:
            release['change_log'] = result['recentChangesHTML']
        except KeyError:
            pass
        return [
            release,
        ]

    def _get_release_list(self, app_id_list: list, auth: dict or None = None):
        for app_id in [
                app_id for app_id in app_id_list
                if android_app_key not in app_id
        ]:
            yield app_id, []
            app_id_list.remove(app_id)
        for lice in [
                app_id_list[i:i + 50] for i in range(0, len(app_id_list), 50)
        ]:
            for app_id, release_list in self.__get_release_list(lice, auth):
                yield app_id, release_list

    def __get_release_list(self, app_id_list: list, auth: dict or None = None):
        # 这里有一处字典转换
        package_list = [_test_package] + [
            app_id[android_app_key] for app_id in app_id_list
        ]
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
        if details_map[_test_package] is None:
            api = self.__get_def_google_play()
            bulk_details = api.bulkDetails(package_list)
            for i, l_details in enumerate(bulk_details):
                package = package_list[i]
                details_map[package] = l_details
        for package, details in details_map.items():
            # 这里有一处字典重组
            # 注意与上面的列表一一对应
            app_id = {android_app_key: package}
            if details is None:
                if app_id in app_id_list:
                    yield app_id, []
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
                    release_list = [
                        release,
                    ]
                except Exception:
                    release_list = None
                if app_id in app_id_list:
                    yield app_id, release_list

    def get_download_info(self,
                          app_id: dict,
                          asset_index: list,
                          auth: dict or None = None) -> tuple or None:
        pass

    def _get_download_info(self,
                           app_id: dict,
                           asset_index: list,
                           auth: dict or None = None) -> tuple or None:
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
                download = self.__auto_download(doc_id, api)
            except Exception:
                api = self.__get_def_google_play(True)
                download = self.__auto_download(doc_id, api)
        main_apk_file = download['file']
        download_list.append({
            "name": f'{doc_id}.apk',
            "url": main_apk_file['url'],
            "headers": main_apk_file['headers'],
            "cookies": main_apk_file['cookies']
        })
        splits_apk_file = download['splits']
        for apk in splits_apk_file:
            apk_file = apk['file']
            download_list.append({
                "name": f"{apk['name']}.apk",
                "url": apk_file['url'],
                "headers": apk_file['headers'],
                "cookies": apk_file['cookies']
            })
        for obb in download['additionalData']:
            obb_file = obb['file']
            obb_file_name = obb['type'] + '.' + str(
                obb['versionCode']) + '.' + download['docId'] + '.obb'
            download_list.append({
                "name": obb_file_name,
                "url": obb_file['url'],
                "headers": obb_file['headers'],
                "cookies": obb_file['cookies']
            })
        return download_list

    @staticmethod
    def __auto_download(doc_id, api):
        detail = api.details(doc_id)
        if detail['offer'][0]['checkoutFlowRequired']:
            method = api.delivery
        else:
            method = api.download
        return method(doc_id, expansion_files=True)

    def __get_google_api(self, auth: dict):
        if auth:
            gsf_id, auth_sub_token = self.__get_auth(auth)
        else:
            auth = self.__get_cache_auth()
            if auth:
                gsf_id, auth_sub_token = auth
            else:
                return self.__get_def_google_play()
        return self.__init_google_play_by_gsfid_and_token(
            auth_sub_token, gsf_id)

    def __get_def_google_play(self, random=False) -> _GooglePlayAPI:
        position = 0
        if random:
            # logging.warn("GooglePlay: Try Random Aurora API")
            position = -1
        email, token = _get_aurora_token(position)
        api = self.__init_google_play_by_email_and_token(email, token)
        add_tmp_cache(
            _auth_cache_key,
            json.dumps({
                "gsfId": api.gsfId,
                "ac2dmToken": api.authSubToken
            }).encode())
        logging.info("GooglePlay: Renew Auth")
        return api

    @staticmethod
    def __init_google_play_by_account(mail: str,
                                      passwd: str) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale,
                            timezone=_timezone,
                            device_codename=_device_codename)
        api.login(mail, passwd)
        return api

    @staticmethod
    def __init_google_play_by_gsfid_and_token(auth_sub_token: str,
                                              gsf_id: int) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale,
                            timezone=_timezone,
                            device_codename=_device_codename)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        return api

    @staticmethod
    def __init_google_play_by_email_and_token(
            email: str, ac2dm_token: str) -> _GooglePlayAPI:
        api = GooglePlayAPI(locale=_locale,
                            timezone=_timezone,
                            device_codename=_device_codename)
        api.gsfId = api.checkin(email, ac2dm_token)
        api.setAuthSubToken(ac2dm_token)
        api.uploadDeviceConfig()
        return api

    def __get_cache_auth(self) -> tuple or None:
        try:
            auth = get_tmp_cache(_auth_cache_key).decode()
        except AttributeError:
            auth = None
        if auth:
            auth_json = json.loads(auth)
            return self.__get_auth(auth_json)
        else:
            return None

    @staticmethod
    def __get_auth(auth: dict):
        return int(auth["gsfId"]), auth["ac2dmToken"]

    @property
    def available_test_url(self) -> str:
        return "https://google.com/"


# 使用了 Aurora 公共帐号接口，感谢 AuroraStore 项目及其开发者 whyorean
_aurora_token_api_url_list = ("https://auroraoss.com/api/auth", )


def _get_aurora_token(index: int) -> tuple:
    if index == -1:
        index = randrange(0, len(_aurora_token_api_url_list))
    aurora_token_api_url = _aurora_token_api_url_list[index]
    data_json = requests.get(aurora_token_api_url).json()
    email = data_json["email"]
    token = data_json["auth"]
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
            headers[
                "X-DFE-Device-Checkin-Consistency-Token"] = self.deviceCheckinConsistencyToken
        if self.dfeCookie is not None:
            headers["X-DFE-Cookie"] = self.dfeCookie
        return headers

    # noinspection PyPep8Naming
    def download(self,
                 packageName,
                 versionCode=None,
                 offerType=1,
                 expansion_files=False):
        """
        避免 Unexpected end-group tag. 错误
        参考：https://github.com/NoMore201/googleplay-api/issues/132
        """

        if self.authSubToken is None:
            raise LoginError("You need to login before executing any request")

        if versionCode is None:
            # pick up latest version
            appDetails = self.details(packageName).get('details').get(
                'appDetails')
            versionCode = appDetails.get('versionCode')

        headers = self.getHeaders()
        params = {
            'ot': str(offerType),
            'doc': packageName,
            'vc': str(versionCode)
        }
        response = requests.post(PURCHASE_URL,
                                 headers=headers,
                                 params=params,
                                 verify=ssl_verify,
                                 timeout=60,
                                 proxies=self.proxies_config)

        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)
        else:
            dlToken = response.payload.buyResponse.downloadToken
            return self.delivery(packageName,
                                 versionCode,
                                 offerType,
                                 dlToken,
                                 expansion_files=expansion_files)

    def _deliver_data(self, url, cookies):
        headers = self.getHeaders()
        return {"url": url, "headers": headers, "cookies": cookies}
