from passlib.hash import pbkdf2_sha512
import re
from dateutil import tz
from itertools import chain, combinations

__author__ = 'abilgin'

class Utils(object):

    # @staticmethod
    def hash_password(self, password):
        """
        Hashes a password using pbkdf2_sha512
        :param password: The sha512 password from the login/register form
        :return: A sha512->pbkdf2_sha512 encrypted password
        """
        return pbkdf2_sha512.encrypt(password)

    # @staticmethod
    def check_hashed_password(self, password, hashed_password):
        """
        Checks that the password the user sent matches that of the database.
        The database password is encrypted more than the user's password at this stage.
        :param password: sha512-hashed password
        :param hashed_password: pbkdf2_sha512 encrypted password
        :return: True if passwords match, False otherwise
        """
        return pbkdf2_sha512.verify(password, hashed_password)

    # @staticmethod
    def email_is_valid(self, email):
        email_address_matcher = re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        return True if email_address_matcher.match(email) else False

    # @staticmethod
    def str_to_bool(self, s):
        if s.lower() == 'true':
             return True
        elif s.lower == 'false':
             return False

    # @staticmethod
    def get_local_display_time(self, timestamp):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = timestamp.replace(tzinfo=from_zone)
        # Convert time zone
        return utc.astimezone(to_zone)

    def powerset(self, iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        # s = list(iterable)  # allows duplicate elements
        s = list(set(iterable))
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))



