from .appchina import AppChina
from .coolapk import CoolApk
from .fdroid import FDroid
from .github import Github
from .sjly import Sjly
from .xp_mod_repo import XpModRepo

hub_dict = {
    "fd9b2602-62c5-4d55-bd1e-0d6537714ca0": Github(),
    "6a6d590b-1809-41bf-8ce3-7e3f6c8da945": FDroid(),
    "1c010cc9-cff8-4461-8993-a86cd190d377": CoolApk(),
    "4a23c3a5-8200-40bb-b961-c1bb5d7fd921": AppChina(),
    "1c010cc9-cff8-4461-8993-a86mm190d377": Sjly(),
    "e02a95a2-af76-426c-9702-c4c39a01f891": XpModRepo()
}
