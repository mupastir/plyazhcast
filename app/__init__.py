import os

from flask import Flask, session, g

from app.admin.views import admin_bp
from app.views import podcast_bp
from app.database import db
from app.models import AdminUser


def _init_login():
    user_id = session.get('user_id')
    print(user_id)

    if user_id is None:
        g.user = None
    else:
        g.user = AdminUser.objects.get(id=user_id)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MONGODB_SETTINGS={
            'db': 'plyazhcast',
            'username': 'root',
            'password': 'example',
            'host': 'localhost',
            'port': 27017,
            'alias': 'default'
        },
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
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
    
    return app
