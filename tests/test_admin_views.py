import pytest
from flask import g, session
from werkzeug.security import generate_password_hash

from app.models import AdminUser


@pytest.fixture
def admin_fixture():
    admin_user = AdminUser(
        email="test@admin.com", password_hash=generate_password_hash("test_password")
    )
    admin_user.save()
    return admin_user


class AdminActions:
    def __init__(self, client):
        self._client = client

    def get_login_page(self):
        return self._client.get("/admin/login")

    def login(self, username, password):
        return self._client.post(
            "/admin/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.post("/admin/logout")

    def get_create_episode_page(self):
        return self._client.get("/admin/create")

    def add_new_episode(
        self, title: str, audio: bytes, cover_image: bytes, themes: str
    ):
        return self._client.post(
            "/admin/create",
            data={
                "title": title,
                "audio": audio,
                "cover_image": cover_image,
                "themes": themes,
            },
        )


@pytest.fixture
def admin_actions(client):
    return AdminActions(client)


def test_login(admin_actions, client, admin_fixture):
    assert admin_actions.get_login_page().status_code == 200
    response = admin_actions.login(username="test@admin.com", password="test_password")
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == str(admin_fixture.id)
        assert g.user["email"] == "test@admin.com"

    response = admin_actions.logout()
    assert response.headers["Location"] == "/"
    with client:
        client.get("/")
        assert session.get("user_id") is None
        assert g.user is None


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        (
            "",
            "",
            b"{&#39;username&#39;: [&#39;This field is required.&#39;], &#39;password&#39;: [&#39;This field is required.&#39;]}",
        ),
        ("test", "", b"{&#39;password&#39;: [&#39;This field is required.&#39;]}"),
        ("test", "123", b"Incorrect username."),
        ("test@admin.com", "123", b"Incorrect password."),
    ),
)
def test_login_validate_input(
    admin_actions, client, admin_fixture, username, password, message
):
    response = admin_actions.login(username, password)
    assert message in response.data
