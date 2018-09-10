import json
from datetime import date

from bson import ObjectId
from flask.json import JSONEncoder


# Adds support for Mongo ObjectIDs & better date format
class _JSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            if isinstance(obj, ObjectId):
                return {
                    '__type__': '__objectid__',
                    'id': str(obj)
                }
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def _decoder(obj):
    if '__type__' in obj and obj['__type__'] == '__objectid__':
            return ObjectId(obj['id'])
    return obj


# Encoder function
def _dumps(obj):
    return json.dumps(obj, cls=_JSONEncoder)


# Decoder function
def _loads(obj):
    return json.loads(obj, object_hook=_decoder)
