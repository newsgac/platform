import pytest

from newsgac.data_sources.models import DataSource


@pytest.fixture()
def data_source_balanced_100(test_user, dataset_balanced_100):
    DataSource.objects.all().delete()
    data_source = DataSource(
        user=test_user,
        filename="bla.txt",
        description="For testing",
        display_title="test dataset",
        file=dataset_balanced_100
    )
    data_source.save()
    return data_source
