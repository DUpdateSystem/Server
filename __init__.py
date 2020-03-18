import sys

if '__main__' in sys.modules:
    sys.modules['__mp_main__'] = sys.modules['__main__']
