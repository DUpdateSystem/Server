import os
import sys

__all__ = ['hub_script_utils', ]

if '__main__' in sys.modules:
    lib_path = os.path.abspath(os.path.join('..'))
    sys.path.append(lib_path)
