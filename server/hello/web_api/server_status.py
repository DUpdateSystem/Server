from flask import Blueprint

from app.status_checker.status import get_redis_availability, __hub_available_key_list

server_status_page = Blueprint('server_status_page', __name__)


@server_status_page.route('/server/status_check')
def check_status():
    if not get_redis_availability():
        return "no redis connect", 503
    elif len(__hub_available_key_list) == 0:
        return "no hub available", 503
    else:
        return '', 204
