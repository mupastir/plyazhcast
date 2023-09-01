import os
from datetime import datetime

import mongomock
import pytest
from mongoengine import connect, disconnect

from app import create_app
from app.models import Episode
from app.utils import timezone as tz

os.environ.setdefault("ENV_FILES", "tests/.env")


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    disconnect()
    connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
    )
    yield app
    disconnect()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def episode():
    episode = Episode(
        title="Test episode",
        themes=["Theme 1", "Theme 2", "Theme 3"],
        mp3_url="http://localhost/static/uploads/audio/intro.mp3",
        cover_url="http://localhost/static/uploads/audio/intro.mp3",
        date_created=datetime.now(tz),
    )
    episode.save()
    return episode
