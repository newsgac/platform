import pytest
from src.app import app as flask_app

@pytest.fixture
def client():
    _client = flask_app.test_client()

    def login(username, password):
        return _client.post('/users/login', data=dict(
            identifier=username,
            password=password
        ), follow_redirects=True)

    def logout():
        return _client.get('/users/logout', follow_redirects=True)

    _client.login = login
    _client.logout = logout

    yield _client


@pytest.fixture
def app():
    return flask_app
