class CacheBankException(Exception):
    """Base class for all exceptions related to the Cache Bank."""
    pass

class CacheBankConstructionError(CacheBankException):
    """Raised when there is an error in constructing the Cache Bank."""
    pass

class CacheBankGetError(CacheBankException):
    """Raised when there is an error in getting data from the Cache Bank."""
    pass

class CacheBankSetError(CacheBankException):
    """Raised when there is an error in setting data in the Cache Bank."""
    pass

class CacheBankMagicMethodError(CacheBankException):
    """Raised when there is an error related to the magic methods in the Cache Bank."""
    pass

class CacheBankUtilsError(CacheBankException):
    """Raised when there is an error in the utility functions of the Cache Bank."""
    pass

class CacheBankMakeHashableError(CacheBankException):
    """Raised when there is an error in making an object hashable for the Cache Bank."""
    pass

class CacheBankSaveError(CacheBankException):
    """Raised when there is an error in saving data to the Cache Bank."""
    pass

class CacheBankLoadError(CacheBankException):
    """Raised when there is an error in loading data from the Cache Bank."""
    pass

class CacheBankRemoveError(CacheBankException):
    """Raised when there is an error in removing data from the Cache Bank."""
    pass

class CacheBankWrapperError(CacheBankException):
    """Raised when there is an error in the Cache Bank wrapper."""
    pass

class CacheBankConfigError(CacheBankException):
    """Raised when there is an error in the configuration of the Cache Bank."""
    pass

class CacheBankAsyncSaveError(CacheBankException):
    """Raised when there is an error in asynchronously saving data to the Cache Bank."""
    pass

class CacheBankAsyncLoadError(CacheBankException):
    """Raised when there is an error in asynchronously loading data from the Cache Bank."""
    pass