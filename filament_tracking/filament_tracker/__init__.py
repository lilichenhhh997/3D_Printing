import threading
import webbrowser
import os as _os
from flask import Flask

from .config import Config
from .db import init_db
from .routes import register_routes


def _open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)
    register_routes(app)

    # 避免 debug 模式下打开两次浏览器
    if _os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, _open_browser).start()

    return app
