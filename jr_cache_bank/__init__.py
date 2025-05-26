"""
jr_cache_bank
=================
A simple caching library for Python, designed to be easy to use and flexible.
It provides a cache bank that can store multiple caches with different configurations,
and a cache reporter to track cache hits and misses.

Some Features:
---------

- Simple and easy to use API.
- Supports multiple cache types (pickle, zlib, gzip, json, yaml).
- Thread-safe and process-safe.

Classes:
---------

- CacheReporter: A class for reporting cache hits and misses.
- CacheBank: A bank of caches, allowing for multiple caches with different configurations.
- CacheType: A enum for different cache save strategies - (PICKLE, ZLIB, GZIP, JSON, YAML).
- CacheSize: A enum for different cache sizes - (E_128KB ... E_16MB).
"""

from jr_cache_bank.cache.cache_reporter import CacheReporter
from jr_cache_bank.cache.cache_bank import CacheBank
from jr_cache_bank.cache.cache_enums import CacheType, CacheSize

__all__ = [
    "CacheReporter",
    "CacheBank",
    "CacheType",
    "CacheSize"
]

__name__ = "jr_cache_bank"
__version__ = "0.1.0"