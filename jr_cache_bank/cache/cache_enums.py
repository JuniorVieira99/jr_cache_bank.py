# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

from enum import Enum, IntEnum, StrEnum

# -------------------------------------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------------------------------------

class CacheType(StrEnum):
    """
    CacheType
    ==========
    An enumeration of the different types of cache.

    Attributes:
        PICKLE (str) :
            The cache type is pickle.
        ZLIB (str) :
            The cache type is zlib.
        GZIP (str) :
            The cache type is gzip.
        JSON (str) :
            The cache type is json.
    """
    PICKLE = ".pkl"
    ZLIB = ".zlib"
    GZIP = ".gz"
    JSON = ".json"
    YAML = ".yaml"

class CacheSize(IntEnum):
    """
    CacheSize
    ==========
    An enumeration of the different cache sizes.

    The formats are as follows is E_*KB or E_*MB, where <size> is the size of the cache in KB or MB.
    The size is in bytes, so 1 KB = 1024 bytes and 1 MB = 1024 * 1024 bytes.

    Attributes:
        E_1KB (int) :
            1 KB
        E_2KB (int) :
            2 KB
        E_4KB (int) :
            4 KB
        E_8KB (int) :
            8 KB
        E_10KB (int) :
            10 KB
        E_16KB (int) :
            16 KB
        E_32KB (int) :
            32 KB
        E_64KB (int) :
            64 KB
        E_128KB (int) :
            128 KB
        E_256KB (int) :
            256 KB
        E_512KB (int) :
            512 KB
        E_1MB (int) :
            1 MB
        E_2MB (int) :
            2 MB
        E_4MB (int) :
            4 MB
        E_8MB (int) :
            8 MB
        E_10MB (int) :
            10 MB
        E_16MB (int) :
            16 MB
        E_32MB (int) :
            32 MB
    """
    
    E_1KB = 1024
    E_2KB = 2 * E_1KB
    E_4KB = 4 * E_1KB
    E_8KB = 8 * E_1KB
    E_10KB = 10 * E_1KB
    E_16KB = 16 * E_1KB
    E_32KB = 32 * E_1KB
    E_64KB = 64 * E_1KB
    E_128KB = 128 * E_1KB
    E_256KB = 256 * E_1KB
    E_512KB = 512 * E_1KB
    E_1MB = 1024 * 1024
    E_2MB = 2 * E_1MB
    E_4MB = 4 * E_1MB
    E_8MB = 8 * E_1MB
    E_10MB = 10 * E_1MB
    E_16MB = 16 * E_1MB
    E_32MB = 32 * E_1MB

