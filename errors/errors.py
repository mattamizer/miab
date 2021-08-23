class EvictionsError(Exception):
    """Raised when things are getting evicted"""

    pass


class CorruptDataError(Exception):
    """Raised when things are getting evicted"""

    pass


class InvalidKeyError(Exception):
    """Exception for when a cache key is invalide
    Attributes:
        key: the key which caused the error
        message: the error message
    """

    def __init__(self, key, message="Key is invalid for use"):
        self.key = key
        self.message = message
        super().__init__(self.message)


class FileTooLargeError(Exception):
    """Exception for file sizes exceeding 50MB
    Attributes:
        file: the file which caused the error
        message: the error message
    """

    def __init__(self, file, message="File exceeds 50MB limit"):
        self.file = file
        self.message = message
        super().__init__(self.message)


class KeyExistsError(Exception):
    """Exception for when a cache key already exists
    Attributes:
        key: the key which caused the error
        message: the error message
    """

    def __init__(self, key, message="Key already exists in cache"):
        self.key = key
        self.message = message
        super().__init__(self.message)


class NoSuchKeyError(Exception):
    """Exception for when a cache key does not exist. Only used for retrieval.
    Attributes:
        key: the key which caused the error
        message: the error message
    """

    def __init__(self, key, message="Key does not exist in cache"):
        self.key = key
        self.message = message
        super().__init__(self.message)


class FileCollisionError(Exception):
    """Exception for when a file has already been added to the cache
    Attributes:
        file: the file which caused the error
        message: the error message
    """

    def __init__(self, filename, message="File already exists in the cache"):
        self.filename = filename
        self.message = message
        super().__init__(self.message)
