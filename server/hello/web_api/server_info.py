from quart import Blueprint

server_info_page = Blueprint('server_info_page', __name__)


@server_info_page.route('/htcpcp')
async def just_can_not_htcpcp():
    return "I'm not a teapot", 406


@server_info_page.route('/about')
async def about():
    return 'DUpdateSystem(UpgradeAll) update server.', 200
