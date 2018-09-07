import pytest
from pymodm.errors import ValidationError

from newsgac.data_sources.models import DataSource


def test_create():
    data_source = DataSource(filename="bla.txt", display_title="test dataset")
    data_source.save()
    assert data_source.created is not None


def test_create_same_name_fails():
    data_source = DataSource(filename="bla2.txt", display_title="test dataset")
    with pytest.raises(ValidationError):
        data_source.save()

