import sys
from app.run import run
from app.server.utils import logging

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        logging.info("手动停止")
        sys.exit(0)
