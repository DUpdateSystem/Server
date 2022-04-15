from quart import Quart

from .server_info import server_info_page
from .server_status import server_status_page
from .update_server import update_server_page
from .cache import regist_cache

app = Quart(__name__)

regist_cache(app)
app.register_blueprint(update_server_page)
app.register_blueprint(server_info_page)
app.register_blueprint(server_status_page)
