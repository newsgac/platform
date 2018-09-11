import os
import sys

import pytest
from newsgac.app import app as flask_app
from pymodm.connection import _get_db


@pytest.fixture
def client():
    _client = flask_app.test_client()

    def login(username='test@test.com', password='testtesttest'):
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
    app_context = flask_app.test_request_context()
    app_context.push()
    yield flask_app


@pytest.fixture(scope="session")
def db():
    yield _get_db()


@pytest.fixture(scope="module", autouse=True)
def setup_db(db):
    # drops whole db
    for collection_name in db.collection_names():
        db[collection_name].drop()


@pytest.fixture(scope="module")
def test_user(db):
    # creates a user 'test@test.com'
    from newsgac.users.models import User
    user = User(email='test@test.com', password='testtesttest', name='Test', surname='User')
    user.save()
    return user


@pytest.yield_fixture()
def dataset_balanced_100():
    with open(os.path.join(sys.path[0], 'test', 'mocks', 'balanced_label_date_100.txt'), 'r') as f:
        yield f
