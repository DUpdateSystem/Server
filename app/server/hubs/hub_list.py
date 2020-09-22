from app.server.hubs.library.appchina import AppChina
from app.server.hubs.library.coolapk import CoolApk
from app.server.hubs.library.fdroid import FDroid
from app.server.hubs.library.github import Github
from app.server.hubs.library.gitlab import Gitlab
from app.server.hubs.library.google_play import GooglePlay
from app.server.hubs.library.sjly import Sjly
from app.server.hubs.library.xp_mod_repo import XpModRepo
from app.server.hubs.library.zlive_official import ZLiveOfficial

hub_dict = {
    "fd9b2602-62c5-4d55-bd1e-0d6537714ca0": Github(),
    "a84e2fbe-1478-4db5-80ae-75d00454c7eb": Gitlab(),
    "6a6d590b-1809-41bf-8ce3-7e3f6c8da945": FDroid(),
    "65c2f60c-7d08-48b8-b4ba-ac6ee924f6fa": GooglePlay(),
    "1c010cc9-cff8-4461-8993-a86cd190d377": CoolApk(),
    "4a23c3a5-8200-40bb-b961-c1bb5d7fd921": AppChina(),
    "1c010cc9-cff8-4461-8993-a86mm190d377": Sjly(),
    "e02a95a2-af76-426c-9702-c4c39a01f891": XpModRepo(),
    "28591e65-849f-4417-aead-9d9098520eed": ZLiveOfficial(),
}

hub_url_dict = {
    "google-play": GooglePlay(),
}
