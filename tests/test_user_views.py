import pytest


class UnauthorizedUserActions:
    def __init__(self, client):
        self._client = client

    def get_main_page(self):
        return self._client.get("/")

    def get_info_page(self):
        return self._client.get("/info")

    def get_rss_feed(self):
        return self._client.get("/feed")


@pytest.fixture
def user_actions(client):
    return UnauthorizedUserActions(client)


def test_user_pages(user_actions, episode):
    response = user_actions.get_main_page()
    assert response.status_code == 200
    assert response.data is not None
    assert b"Test episode" in response.data
    assert b"Theme 1" in response.data
    assert b"Theme 2" in response.data
    assert b"Theme 3" in response.data

    response = user_actions.get_info_page()
    assert response.status_code == 200
    assert response.data is not None

    response = user_actions.get_rss_feed()
    assert response.status_code == 200
    assert response.data is not None
    assert b"Test episode" in response.data
    assert b"Theme 1" in response.data
    assert b"Theme 2" in response.data
    assert b"Theme 3" in response.data
