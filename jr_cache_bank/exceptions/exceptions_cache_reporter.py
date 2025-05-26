class CacheReporterException(Exception):
    """Base class for exceptions in this module."""
    pass

class CacheReporterConstructionError(CacheReporterException):
    """Exception raised for errors in the construction of the cache reporter."""
    pass

class CacheReporterPropertyError(CacheReporterException):
    """Exception raised for errors in getting data from the cache."""
    pass

class CacheReporterMagicMethodError(CacheReporterException):
    """Exception raised for errors in the magic methods of the cache reporter."""
    pass

class CacheReporterAddFunctionError(CacheReporterException):
    """Exception raised for errors in the add function of the cache reporter."""
    pass

class CacheReporterDellFunctionError(CacheReporterException):
    """Exception raised for errors in the delete function of the cache reporter."""
    pass

class CacheReporterGetFunctionError(CacheReporterException):
    """Exception raised for errors in the get function of the cache reporter."""
    pass

class CacheReporterSetFunctionError(CacheReporterException):
    """Exception raised for errors in the set function of the cache reporter."""
    pass

class CacheReporterUtilsError(CacheReporterException):
    """Exception raised for errors in the utils of the cache reporter."""
    pass
