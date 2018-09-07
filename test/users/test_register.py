from newsgac.users.models import User
from test.helpers import is_valid_html


def test_page_loads(client):
    rv = client.get('/users/register')
    assert rv.status_code == 200
    assert is_valid_html(rv.data)


def test_empty_register(client):
    rv = client.post('/users/register', data=dict(
    ))
    assert rv.status_code == 200


def test_register(client):
    rv = client.post('/users/register', data=dict(
        name="Test",
        surname="User",
        email="test@test.com",
        password="test123test",
    ))
    print (rv.data)
    assert rv.status_code == 302
    user = User.objects.get({'_id': 'test@test.com'})
    assert user.name == 'Test'
    assert user.surname == 'User'
    assert user.email == 'test@test.com'
    assert user.password != 'test123test'


def test_register_exists(client):
    rv = client.post('/users/register', data=dict(
        name="Test",
        surname="User",
        email="test@test.com",
        password="test123test",
    ))

    assert rv.status_code == 200
    assert 'already in use' in rv.data
