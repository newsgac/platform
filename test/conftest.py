import os
import sys

import pytest
from newsgac.app import app as flask_app
from pymodm.connection import _get_db
from pathlib import Path

def pytest_addoption(parser):
    parser.addoption(
        "--frog", action="store_true", default=False, help="run tests using frog"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--frog"):
        from newsgac.nlp_tools import tasks
        tasks.worker_name = 'frog_test'
        tasks.setup_frog_conn(None, None)

    skip_frog = pytest.mark.skip(reason="need --frog option to run")
    for item in items:
        if "frog" in item.keywords:
            item.add_marker(skip_frog)



@pytest.fixture
def client():
    flask_app.testing = True
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
    flask_app.testing = True
    yield flask_app


@pytest.fixture(scope="session")
def db():
    yield _get_db()


@pytest.fixture(scope="module", autouse=True)
def setup_db(db):
    # drops whole db
    for collection_name in db.list_collection_names():
        db[collection_name].drop()


@pytest.fixture(scope="module")
def test_user(db):
    # creates ws user 'test@test.com'
    from newsgac.users.models import User
    user = User(email='test@test.com', password='testtesttest', name='Test', surname='User')
    user.save()
    return user


@pytest.yield_fixture()
def dataset_balanced_100():
    file_path = Path(__file__).parent / 'mocks' / 'balanced_label_date_100.txt'
    with open(str(file_path), 'rb') as f:
        yield f

@pytest.yield_fixture()
def dataset_balanced_10():
    file_path = Path(__file__).parent / 'mocks' / 'balanced_label_date_10.txt'
    with open(str(file_path), 'rb') as f:
        yield f
