import json

from passlib.hash import pbkdf2_sha512
import re
from dateutil import tz
from itertools import chain, combinations

from newsgac.common.json_encoder import _dumps

__author__ = 'abilgin'

# @staticmethod
def hash_password(password):
    """
    Hashes a password using pbkdf2_sha512
    :param password: The sha512 password from the login/register form
    :return: A sha512->pbkdf2_sha512 encrypted password
    """
    return pbkdf2_sha512.hash(password)

# @staticmethod
def check_hashed_password(password, hashed_password):
    """
    Checks that the password the user sent matches that of the database.
    The database password is encrypted more than the user's password at this stage.
    :param password: sha512-hashed password
    :param hashed_password: pbkdf2_sha512 encrypted password
    :return: True if passwords match, False otherwise
    """
    return pbkdf2_sha512.verify(password, hashed_password)

def is_hashed_password(password):
    return re.search('^\$pbdkf2-sha512.*$', password) is not None

# @staticmethod
def email_is_valid(email):
    email_address_matcher = re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
    return True if email_address_matcher.match(email) else False

# @staticmethod
def str_to_bool(s):
    if s.lower() == 'true':
         return True
    elif s.lower == 'false':
         return False

# @staticmethod
def get_local_display_time(timestamp):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = timestamp.replace(tzinfo=from_zone)
    # Convert time zone
    return utc.astimezone(to_zone)

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    # s = list(iterable)  # allows duplicate elements
    s = list(set(iterable))
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def model_to_dict(model, remove_cls=True):
    model_dict = model.to_son().to_dict()
    if remove_cls:
        remove_cls_from_dict(model_dict)
    return model_dict


def remove_cls_from_dict(model_dict):
    """
    Remove _cls keys from dict representations of models (they are added by pymodm to_son())
    :param model_dict: the dict representation of a model still containing _cls keys
    """
    if isinstance(model_dict, dict):
        if '_cls' in model_dict:
            del model_dict['_cls']
        for value in model_dict.values():
            remove_cls_from_dict(value)

    if isinstance(model_dict, list):
        for value in model_dict:
            remove_cls_from_dict(value)


def model_to_json(model, **kwargs):
    return _dumps(model_to_dict(model), **kwargs)


def split_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def split_long_sentences(sentences, max_tokens=48):
    new_sentences = []

    for sentence in sentences:
        words = sentence.split(' ')

        while len(words) > max_tokens:
            new_sentences.append(' '.join(words[:max_tokens]) + '.')
            words = words[max_tokens:]

        if len(words) > 0:
           new_sentences.append(' '.join(words))

    return new_sentences
