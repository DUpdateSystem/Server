from .github import Github
from .fdroid import FDroid

hub_dict = {
    "fd9b2602-62c5-4d55-bd1e-0d6537714ca0": Github(),
    "6a6d590b-1809-41bf-8ce3-7e3f6c8da945": FDroid()
}
