import pytest
from newsgac.app import app as flask_app
from pymodm.connection import _get_db


@pytest.fixture
def client():
    _client = flask_app.test_client()

    def login(username='test', password='test'):
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
    yield flask_app


@pytest.fixture(scope="session")
def db():
    yield _get_db()


@pytest.fixture(scope="module", autouse=True)
def setup_db(db):
    # drops whole db, and adds a user 'test'
    for collection_name in db.collection_names():
        db[collection_name].drop()
    from newsgac.users.models import User
    user = User(email='test', password='test')
    user.save(full_clean=False)
