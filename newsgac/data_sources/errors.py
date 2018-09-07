__author__ = 'abilgin'


class ResourceError(Exception):
    def __init__(self, message):
        self.message = message


class ResourceDisplayTitleAlreadyExistsError(ResourceError):
    pass


# class ResourceFilenameAlreadyExistsError(ResourceError):
#     pass


# class ResourceAlreadyExistsError(ResourceError):
#     pass

#
# class ProcessingConfigAlreadyExists(ResourceError):
#     pass