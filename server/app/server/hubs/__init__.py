import importlib
import os
import sys
from pathlib import Path

root_module_name = 'app.server.hubs'
module_name = 'library'

library_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__))), module_name)
for file in library_path.glob("*.py"):
    importlib.import_module(f'{root_module_name}.{module_name}.{file.stem}')

__all__ = ['hub_script_utils', ]

if '__main__' in sys.modules:
    lib_path = os.path.abspath(os.path.join('..'))
    sys.path.append(lib_path)
