__author__ = 'abilgin'

class ConfigError(Exception):
    def __init__(self, message):
        self.message = message

class ConfigAlreadyExistsError(ConfigError):
    pass