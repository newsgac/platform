import pytest
from pymodm.errors import ValidationError

from src.models.users.user import User


def test_invalid_email():
    user = User(email='test', password='testtesttest')
    with pytest.raises(ValidationError):
        user.save()


def test_invalid_password():
    user = User(email='test@test.com', password='test')
    with pytest.raises(ValidationError):
        user.save()


def test_password_is_hashed():
    password = 'testtesttest'
    user = User(email='test@test.com', password=password)
    user.save()
    user.refresh_from_db()
    assert user.password != password
