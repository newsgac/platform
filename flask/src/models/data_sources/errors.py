__author__ = 'abilgin'

class ResourceError(Exception):
    def __init__(self, message):
        self.message = message

class ResourceAlreadyExistsError(ResourceError):
    pass
