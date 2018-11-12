import pytest
from pymodm.errors import ValidationError

from newsgac.users.models import User


def test_invalid_email():
    user = User(email='test', password='testtesttest')
    with pytest.raises(ValidationError):
        user.save()


def test_invalid_password():
    user = User(email='testuser@test.com', password='test')
    with pytest.raises(ValidationError):
        user.save()


def test_password_is_hashed():
    password = 'testtesttest'
    user = User(email='testuser@test.com', password=password, name='Test', surname='User')
    user.save()
    user.refresh_from_db()
    assert user.password != password
    user.delete()
