from flask import Blueprint

server_info_page = Blueprint('server_info_page', __name__)


@server_info_page.route('/htcpcp')
def just_can_not_htcpcp():
    return "I'm not a teapot", 406


@server_info_page.route('/about')
def about():
    return 'DUpdateSystem(UpgradeAll) update server.', 200
