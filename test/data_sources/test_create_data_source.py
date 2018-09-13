import pytest
from pymodm.errors import ValidationError

from newsgac.data_sources.models import DataSource


def test_create(test_user, dataset_balanced_100):
    data_source = DataSource(
        user=test_user,
        filename="bla.txt",
        description="For testing",
        display_title="test dataset",
        file=dataset_balanced_100
    )
    data_source.save()
    assert data_source.created is not None


def test_create_same_name_fails(test_user, dataset_balanced_100):

    data_source = DataSource(
        user=test_user,
        filename="bla.txt",
        description="For testing",
        display_title="test dataset",
        file=dataset_balanced_100
    )
    with pytest.raises(ValidationError):
        data_source.save()

