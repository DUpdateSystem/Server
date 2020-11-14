import importlib
import inspect
import os
import sys
from pathlib import Path

from . import library
from .base_hub import BaseHub
from .library.xp_mod_repo import XpModRepo

root_module_name = 'app.server.hubs'
module_name = 'library'


def try_instantiate_cls(cls):
    # noinspection PyBroadException
    try:
        cls()
    except Exception:
        pass


library_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__))), module_name)
for file in library_path.glob("*.py"):
    cls_list = inspect.getmembers(importlib.import_module(f'{root_module_name}.{module_name}.{file.stem}'),
                                  inspect.isclass)
    for cls in cls_list:
        try_instantiate_cls(cls)

__all__ = ['hub_script_utils', ]

if '__main__' in sys.modules:
    lib_path = os.path.abspath(os.path.join('..'))
    sys.path.append(lib_path)
