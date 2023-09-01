import os

from flask import Flask, g, session
from flask_wtf.csrf import CSRFProtect

from app.admin.views import admin_bp
from app.database import db
from app.models import AdminUser
from app.views import podcast_bp

csrf = CSRFProtect()


def _init_login():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = AdminUser.get_by_id(admin_id=user_id)


def create_app(test_config=None):
    from .config import get_settings

    settings = get_settings()
    # create and configure the app
    os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(**settings.model_dump())

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(admin_bp)
    app.register_blueprint(podcast_bp)
    app.before_request(_init_login)
    csrf.init_app(app)

    return app
