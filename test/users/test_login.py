def test_login_logout(test_user, client):
    """Make sure login and logout works."""

    rv = client.login()
    assert b'You were successfully logged in.' in rv.data

    rv = client.logout()
    assert b'You were successfully logged out.' in rv.data


def test_login_wrong_username(client):
    rv = client.login('abc', '123')
    assert b'User not found or password incorrect' in rv.data


def test_login_wrong_password(client):
    rv = client.login('test@test.com', '123')
    assert b'User not found or password incorrect' in rv.data
