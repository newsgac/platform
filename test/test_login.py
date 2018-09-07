def test_login_logout(client):
    """Make sure login and logout works."""

    rv = client.login('test', 'test')
    assert b'You were successfully logged in.' in rv.data

    rv = client.logout()
    assert b'You were successfully logged out.' in rv.data

    rv = client.login('abc', '123')
    assert b'The username/email does not exist' in rv.data

    rv = client.login('test', '123')
    assert b'The password is incorrect.' in rv.data
