def test_login_logout(test_user, client):
    """Make sure login and logout works."""

    rv = client.login()
    if not b'You were successfully logged in.' in rv.data: raise AssertionError()

    rv = client.logout()
    if not b'You were successfully logged out.' in rv.data: raise AssertionError()


def test_login_wrong_username(client):
    rv = client.login('abc', '123')
    if not b'User not found or password incorrect' in rv.data: raise AssertionError()


def test_login_wrong_password(client):
    rv = client.login('test@test.com', '123')
    if not b'User not found or password incorrect' in rv.data: raise AssertionError()
