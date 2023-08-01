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
        g.user = AdminUser.objects.get(id=user_id)


def create_app(test_config=None):
    # create and configure the app
    base_path = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        TITLE=os.environ.get("TITLE", "Пляжкаст"),
        BASE_PATH=base_path,
        IMAGE_UPLOAD_PATH=os.environ.get("IMAGE_UPLOAD_PATH", "/static/uploads/images"),
        AUDIO_UPLOAD_PATH=os.environ.get("AUDIO_UPLOAD_PATH", "/static/uploads/audio"),
        WTF_CSRF_SECRET_KEY=os.environ.get("WTF_CSRF_SECRET_KEY", "test"),
        HOST=os.environ.get("HOST", "http://localhost:8080"),
        MONGODB_SETTINGS={
            "db": os.environ.get("DB_NAME", "plyazhcast"),
            "username": os.environ.get("DB_USER", "root"),
            "password": os.environ.get("DB_PASSWORD", "example"),
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", 27017),
            "alias": "default",
        },
    )

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
