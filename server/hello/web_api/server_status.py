from quart import Blueprint

server_status_page = Blueprint('server_status_page', __name__)


@server_status_page.route('/server/status_check')
async def check_status():
    # 暂无其他
    return '', 204
