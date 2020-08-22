from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id
from gpapi.googleplay import GooglePlayAPI

locale = "en_US"
timezone = "UTC"
device_codename = "oneplus3"


class GooglePlay(BaseHub):
    def init_account(self, account_id: list) -> tuple or None:
        mail, passwd = _get_account(account_id)

        api = GooglePlayAPI(locale=locale, timezone=timezone, device_codename=device_codename)
        api.login(email=mail, password=passwd)
        return {
            "gsfId": api.gsfId,
            "authSubToken": api.authSubToken
        }

    def get_release_list(self, app_id_list: list) -> tuple or None:
        api = GooglePlayAPI(locale=locale, timezone=timezone, device_codename=device_codename)
        gsf_id, auth_sub_token = _get_token(app_id)
        package = _get_package(app_id)
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        p = api.details(package)
        p.

    def get_download_info(self, app_id: list, asset_index: list) -> dict or None:
        pass


def _get_account(app_info: list) -> tuple:
    return get_value_from_app_id(app_info, "mail"), \
           get_value_from_app_id(app_info, "passwd")


def _get_token(app_info: list) -> tuple:
    return get_value_from_app_id(app_info, "gsfId"), \
           get_value_from_app_id(app_info, "authSubToken")


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
