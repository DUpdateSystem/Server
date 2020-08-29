from ..base_hub import BaseHub
from app.server.manager.asset_manager import write_byte_asset
from gpapi.googleplay import GooglePlayAPI as _GooglePlayAPI

locale = "en_US"
timezone = "UTC"
device_codename = "oneplus3"


class GooglePlay(BaseHub):
    def init_account(self, account: dict) -> dict or None:
        mail = account['mail']
        passwd = account['passwd']
        api = _GooglePlayAPI(locale=locale, timezone=timezone, device_codename=device_codename)
        api.login(email=mail, password=passwd)
        return {
            "gsfId": api.gsfId,
            "authSubToken": api.authSubToken
        }

    def get_release_list(self, app_id_list: list, auth: dict or None = None) -> dict or None:
        app_release_dict = {}
        api = _GooglePlayAPI(locale=locale, timezone=timezone, device_codename=device_codename)
        gsf_id = int(auth['gsfId'])
        auth_sub_token = auth['authSubToken']
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        package_list = [app_id['android_app_package'] for app_id in app_id_list]
        bulk_details = api.bulkDetails(package_list)
        for i, l_details in enumerate(bulk_details):
            app_id = app_id_list[i]
            if l_details is None:
                app_release_dict[frozenset(app_id)] = []
            else:
                # noinspection PyBroadException
                try:
                    package = package_list[i]
                    details = api.details(package)['details']['appDetails']
                    release_list = [{
                        'version_number': details['versionString'],
                        'change_log': details['recentChangesHtml'],
                        'assets': [{
                            'file_name': package + '.apk',
                            'download_url': f'grcp://download.xzos.net/google-play/{package}',
                        }]
                    }, ]
                except Exception:
                    release_list = [None, ]
                app_release_dict[frozenset(app_id)] = release_list
        return app_release_dict

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> tuple or None:
        download_list = []
        doc_id = app_id['android_app_package']
        api = _GooglePlayAPI(locale=locale, timezone=timezone, device_codename=device_codename)
        gsf_id = int(auth['gsfId'])
        auth_sub_token = auth['authSubToken']
        api.gsfId = gsf_id
        api.setAuthSubToken(auth_sub_token)
        download = api.download(doc_id, expansion_files=True)
        apk_file = f'{doc_id}.apk'
        apk_file_url = write_byte_asset(apk_file, download.get('file').get('data'))
        download_list.append((apk_file_url,))
        for obb in download['additionalData']:
            obb_file = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
            obb_file_url = write_byte_asset(obb_file, obb.get('file').get('data'))
            download_list.append((obb_file_url,))
        return download_list
