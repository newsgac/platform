from pymodm.errors import ValidationError, DoesNotExist

# from newsgac.data_sources.models import DataSource

#
# def is_unique(field_name):
#     # todo: is broken (not valid when updating)
#     # todo: circular import (Datasource <-> validators)
#     def test_unique(value):
#         try:
#             DataSource.objects.get({field_name: value})
#             raise ValidationError('%s is not unique: ' % value)
#         except DoesNotExist:
#             pass
#     return test_unique


def has_extension(*extensions):
    def test_extension(value):
        if '.' not in value or value.split('.')[-1].lower() not in extensions:
            raise ValidationError('File extension not allowed')
    return test_extension
