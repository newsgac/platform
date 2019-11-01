from newsgac.users.models import User
from test.helpers import is_valid_html


def test_page_loads(client):
    rv = client.get('/users/register')
    if not rv.status_code == 200: raise AssertionError()
    if not is_valid_html(rv.data.decode('utf-8')): raise AssertionError()


def test_empty_register(client):
    rv = client.post('/users/register', data=dict(
    ))
    if not rv.status_code == 200: raise AssertionError()


def test_register(client):
    rv = client.post('/users/register', data=dict(
        name="Test",
        surname="User",
        email="test@test.com",
        password="test123test",
    ))

    if not rv.status_code == 302: raise AssertionError()
    user = User.objects.get({'_id': 'test@test.com'})
    if not user.name == 'Test': raise AssertionError()
    if not user.surname == 'User': raise AssertionError()
    if not user.email == 'test@test.com': raise AssertionError()
    if not user.password != 'test123test': raise AssertionError()


def test_register_exists(client):
    rv = client.post('/users/register', data=dict(
        name="Test",
        surname="User",
        email="test@test.com",
        password="test123test",
    ))

    if not rv.status_code == 200: raise AssertionError()
    if not 'already in use' in rv.data.decode('utf-8'): raise AssertionError()
