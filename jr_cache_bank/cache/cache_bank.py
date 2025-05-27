"""
Cache Bank
===========

A cache bank for storing and retrieving data using different cache types (pickle, zlib, gzip).

Description:
-----------
    - The CacheBank class implements a cache bank for storing and retrieving data.
    - It uses an OrderedDict to maintain the order of the items.
    - The cache bank can be configured to use LRU (Least Recently Used) eviction policy.
    - The cache bank can be saved to and loaded from a file using pickle, zlib, or gzip.
    - The class is thread-safe and can be used in a multi-threaded environment.

Classes:
-----------
    - CacheType: An enumeration of the different types of cache (pickle, zlib, gzip).
    - CacheBank: A class that implements a cache bank for storing and retrieving data.

Methods:
-----------
    - get: Returns the value associated with the key in the cache bank.
    - set: Sets the value associated with the key in the cache bank.
    - clear: Clears the cache bank.
    - remove: Removes the item associated with the key in the cache bank.
    - items: Returns a list of tuples containing the key-value pairs in the cache bank.
    - keys: Returns a list of keys in the cache bank.
    - values: Returns a list of values in the cache bank.
    - is_full: Returns True if the cache bank is full, False otherwise.
    - is_empty: Returns True if the cache bank is empty, False otherwise.
    - print: Prints the cache bank.
    - save: Saves the cache bank to a file.
    - load: Loads the cache bank from a file.
    - remove_files: Removes the cache bank standard files.
    - wrapper: A decorator that wraps a function to cache its results.

Report Methods:
-----------
    - print_report: Prints the report for the cache bank.
    - print_cache_report: Prints the cache report for the cache bank.
    - print_func_stats: Prints the statistics for a function in the cache bank.
    - print_full_func_stats: Prints the full statistics for all functions in the cache bank.

Example:
-----------
```python
    # make a cache bank
    cache_bank = CacheBank(max_bank_size=10)

    # Manually

    # set cache func
    cache_bank.set("some_func", args=(1, 2), kwargs={"a": 1}, result=3)
    # get cache func
    result = cache_bank.get("some_func", args=(1, 2), kwargs={"a": 1})

    # Wrapper

    # set cache func
    @cache_bank.wrapper()
    def func1(x, y):
        return x + y

    # Use call to cache the function in a wrapper
    def some_function(x, y):
        return x * y

    wrapped_some_function = cache_bank(some_function)

    # Save and load cache bank
    cache_bank.save() # Set filename if necessary
    cache_bank.load() # Set filename if necessary

    # Check if the cache bank is full
    is_full = cache_bank.is_full()
    # Check if the cache bank is empty
    is_empty = cache_bank.is_empty()

    # Print the cache bank
    cache_bank.print()
```
"""

# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import json
import logging
import os
from re import L
import sys
import io
import threading
import asyncio

from pathlib import Path
from functools import partial, wraps

from collections import OrderedDict
from typing import Callable, Any, Dict, List, Optional, Tuple, Union

# Locals
from jr_cache_bank.config.setup_logger import setup_logger
from jr_cache_bank.cache.cache_reporter import CacheReporter
from jr_cache_bank.cache.cache_enums import CacheType, CacheSize
from jr_cache_bank.cache.cache_load_comp import LoadersContainer
from jr_cache_bank.cache.cache_save_comp import ConvertersContainer

from jr_cache_bank.exceptions.exceptions_cache_bank import (
    CacheBankConstructionError,
    CacheBankGetError,
    CacheBankSetError,
    CacheBankMagicMethodError,
    CacheBankUtilsError,
    CacheBankMakeHashableError,
    CacheBankSaveError,
    CacheBankLoadError,
    CacheBankRemoveError,
    CacheBankConfigError,
    CacheBankAsyncSaveError,
    CacheBankAsyncLoadError
)

# -------------------------------------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------------------------------------

try:
    LOGGER: logging.Logger = setup_logger()
    LOGGER.setLevel(logging.INFO)
except Exception as e:
    LOGGER: logging.Logger = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.error(f"Error setting up logger: {e}")

# -------------------------------------------------------------------------------------------------
# CLasses
# -------------------------------------------------------------------------------------------------


class CacheBank:
    """
    CacheBank
    ========
    A class that implements a cache bank for storing and retrieving data.

    Attention:
    ----------
    Loading pickle data is unsafe, only use it if you trust the source of the data.
    If you are using pickle, zlib, or gzip, make sure to use the same cache type when loading the data.

    Notes:
    -------
    - The cache bank is implemented as an OrderedDict, which maintains the order of the items.
    - The LRU eviction policy is implemented by removing the least recently used item when the cache bank is full.
    - The cache bank can be saved to and loaded from a file using the type specified in the cache_type attribute.
    - The class is thread-safe and can be used in a multi-threaded environment.
    - Use the `CacheSize` enum for better readability when setting the maximum sizes of the cache bank.

    Enums:
    -------
        #### CacheType (Enum) :
            An enumeration of the different types of cache (pickle, zlib, gzip).
            - PICKLE: The cache type is pickle. * Unsafe
            - ZLIB: The cache type is zlib.
            - GZIP: The cache type is gzip.
            - JSON: The cache type is JSON.
            - YAML: The cache type is YAML.
        #### CacheSize (Enum) :
            An enumeration of the different cache sizes.
            - E_1KB: 1 KB
            ...
            - E_16MB: 16 MB

    Arguments:
        max_bank_size (int) :
            The maximum size of the cache bank.
            - Default is 100.
        max_total_memory_size (int) :
            The maximum total memory size (bytes) of the cache bank.
            - Default is CacheSize.E_10MB.
        max_func_memory_size (int) :
            The maximum size of a single function (bytes) in the cache bank.
            - Default is CacheSize.E_16KB.
        lru (bool) :
            If True, the cache bank will use LRU (Least Recently Used) eviction policy.
            - Default is True.
        max_file_size (int) :
            The maximum size of the cache bank file.
            - Default is 100000.
        cache_bank (OrderedDict[str, OrderedDict[Tuple, Any]]) :
            The initial cache bank.
            - Default is None.
        filename (str | Path) :
            The name of the file to save the cache bank to.
            - Default is None.
    
    Methods:
    ---------
        ### get(key: Any) :
            Returns the value associated with the key in the cache bank.
        ### set(key: Any, value: Any) :
            Sets the value associated with the key in the cache bank.
        ### clear() :
            Clears the cache bank.
        ### remove(key: Any) :
            Removes the item associated with the key in the cache bank.
        ### items() :
            Returns a list of tuples containing the key-value pairs in the cache bank.
        ### keys() :
            Returns a list of keys in the cache bank.
        ### values() :
            Returns a list of values in the cache bank.
        ### is_full() :
            Returns True if the cache bank is full, False otherwise.
        ### is_empty() :
            Returns True if the cache bank is empty, False otherwise.
        ### save(filename: str | Path | None) :
            Saves the cache bank to a file.
        ### load(filename: str | Path | None) :
            Loads the cache bank from a file.
        ### remove_files():
            Removes the cache bank standard files.
        ### wrapper(func: Callable) :
            A decorator that wraps a function to cache its results.

    Print Methods:
    ----------------
        ### print() :
            Prints the cache bank.
        ### print_report() :
            Prints the report for the cache bank.
        ### print_cache_report() :
            Prints the cache report for the cache bank.
        ### print_func_stats(func: Callable) :
            Prints the statistics for a function in the cache bank.
        ### print_full_func_stats() :
            Prints the full statistics for all functions in the cache bank.

    Configuration Methods:
    --------------------------
        ### config_from_dict(config: Dict[str, Any]) :
            Configures the cache bank from a dictionary.
        ### config_from_json(json_file: str | Path) :
            Configures the cache bank from a JSON file.

    Example:
    -----------
    ```python
        # make a cache bank
        cache_bank = CacheBank(max_bank_size=10)

        # Manually

        # set cache func
        cache_bank.set("some_func", args=(1, 2), kwargs={"a": 1}, result=3)
        # get cache func
        result = cache_bank.get("some_func", args=(1, 2), kwargs={"a": 1})

        # Wrapper

        # set cache func
        @cache_bank.wrapper()
        def func1(x, y):
            return x + y

        # Use call to cache the function in a wrapper
        def some_function(x, y):
            return x * y

        wrapped_some_function = cache_bank(some_function)

        # Async Wrapper

        # set async cache func
        @cache_bank.async_wrapper()
        async def some_function_2(x, y):
            return x + y

        async def some_function_2(x, y):
            return x * y
        
        # Use call to cache the async function in a wrapper
        wrapped_some_function_2 = cache_bank(some_function_2)   

        # Save and load cache bank
        cache_bank.save() # Set filename if necessary
        cache_bank.load() # Set filename if necessary

        # Check if the cache bank is full
        is_full = cache_bank.is_full()
        # Check if the cache bank is empty
        is_empty = cache_bank.is_empty()

        # Print the cache bank
        cache_bank.print()
    ```   
    """

    # -------------
    # Slots

    __slots__ = (
        "_cache_bank",
        "_func_size_dict",
        "_max_bank_size",
        "_max_total_memory_size",
        "_max_func_memory_size",
        "_max_file_size",
        "_lru",
        "_filename",
        "_cache_reporter",
        "_cache_type",
        "_converter_container",
        "_loaders_container",
        "_mutex"
    )

    # -------------
    # Attributes

    _cache_bank: OrderedDict[str, OrderedDict[Tuple, Any]]
    _func_size_dict: Dict[str, CacheSize]
    _max_bank_size: int
    _max_memory_size: int
    _max_total_memory_size: int
    _max_func_memory_size: int
    _max_file_size: int
    _lru: bool
    _filename: Path
    _cache_reporter: CacheReporter
    _cache_type: CacheType
    _converter_container: ConvertersContainer
    _loaders_container: LoadersContainer
    _mutex: Optional[threading.Lock]

    # -------------
    # Constructor

    def __init__(
        self,
        max_bank_size: int = 100,
        max_total_memory_size: int = CacheSize.E_10MB,
        max_func_memory_size: int = CacheSize.E_16KB,
        lru: bool = True,
        max_file_size: int = CacheSize.E_10MB,
        cache_type: CacheType = CacheType.GZIP,
        cache_bank: Optional[OrderedDict[str, OrderedDict[Tuple, Any]]] = None,
        func_size_dict: Optional[Dict[str, CacheSize]] = None,
        filename: Optional[Union[str, Path]] = None,
    ):
        """
        __init__
        ======
        Constructor for the CacheBank class.

        Arguments:
            max_bank_size (int) :
                The maximum size of the cache bank.
                - Default is 100
            max_total_memory_size (int) :
                The maximum total memory size (bytes) of the cache bank.
                - Default is CacheSize.E_10MB.
            max_func_memory_size (int) :
                The maximum size of a single function (bytes) in the cache bank.
                - Default is CacheSize.E_16KB.
            lru (bool) :
                If True, the cache bank will use LRU (Least Recently Used) eviction policy.
                - Default is True.
            max_file_size (int) :
                The maximum size of the cache bank file.
                - Default is CacheSize.E_10MB (10MB).
            cache_type (CacheType) :
                The type of cache to use.
                - Default is CacheType.GZIP.
            cache_bank (Dict[Any, Any]) :
                The initial cache bank.
                - Default is None.
            func_size_dict (Dict[str, CacheSize]) :
                The function size dictionary.
                - This dictionary will applied memory size restriction to the specific func declared
                - Default is None.
                - Example: `{"func_name": CacheSize.E_1MB}`
            filename (str | Path) :
                The name of the file to save the cache bank to.
                - Default is None.
        """
        try:
            super().__init__()

            # Initialize the cache_reporter
            self._cache_reporter = CacheReporter()
            # Initialize the converter_container
            self._converter_container = ConvertersContainer()
            # Initialize the loaders_container
            self._loaders_container = LoadersContainer()

            if filename:
                self.filename = filename
            else:
                # Handle filename
                self.filename = Path(f"jr_cache_bank/cache/dump/cache_bank{cache_type}").resolve()

            if cache_bank is None:
                self.cache_bank = OrderedDict()
            else:
                if not isinstance(cache_bank, OrderedDict):
                    raise TypeError(f"Cache bank must be an OrderedDict, got {type(cache_bank)}")
                self.cache_bank = cache_bank
                
            self.max_bank_size = max_bank_size
            self._max_total_memory_size = max_total_memory_size
            self._max_func_memory_size = max_func_memory_size
            self.lru = lru
            self.max_file_size = max_file_size
            self._mutex= None
            self.cache_type = cache_type

            if self._max_func_memory_size > self._max_total_memory_size:
                raise ValueError("Maximum function memory size must be less than or equal to maximum total memory size.")
            
            if self._max_total_memory_size < self._max_func_memory_size:
                raise ValueError("Maximum total memory size must be greater than or equal to maximum function memory size.")
            
            self.max_total_memory_size = max_total_memory_size
            self.max_func_memory_size = max_func_memory_size
            
            if func_size_dict is None:
                self.func_size_dict = {}
            else:
                self.func_size_dict = func_size_dict

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> initializing CacheBank: {e}")
            raise CacheBankConstructionError(f"Error '{e.__class__.__name__}' -> initializing CacheBank: {e}")
    
    # -------------
    # Properties

    @property
    def cache_bank(self) -> OrderedDict[str, OrderedDict[Tuple, Any]]:
        """
        Returns the cache bank.
        """
        return self._cache_bank
    
    @property
    def func_size_dict(self) -> Dict[str, CacheSize]:
        """
        Returns the function size dictionary.
        """
        return self._func_size_dict

    @property
    def max_bank_size(self) -> int:
        """
        Returns the maximum size of the cache bank.
        """
        if not isinstance(self._max_bank_size, int):
            self._max_bank_size = 0
        return self._max_bank_size
    
    @property
    def max_total_memory_size(self) -> int:
        """
        Returns the maximum total memory size of the cache bank.
        """
        return self._max_total_memory_size

    @property
    def max_func_memory_size(self) -> int:
        """
        Returns the maximum size of a single function in the cache bank.
        """
        return self._max_func_memory_size

    @property
    def max_file_size(self) -> int:
        """
        Returns the maximum size of the cache bank file.
        """
        return self._max_file_size
    
    @property
    def lru(self) -> bool:
        """
        Returns True if the cache bank is using LRU (Least Recently Used) eviction policy.
        """
        return self._lru

    @property
    def filename(self) -> Path:
        """
        Returns the filename of the cache bank.
        """
        return self._filename
    
    @property
    def bank_length(self) -> int:
        """
        Returns the length of the cache bank.
        """
        return len(self.cache_bank)

    @property
    def cache_type(self) -> CacheType:
        """
        Returns the cache reporter.
        """
        return self._cache_type

    @property
    def mutex(self) -> threading.Lock:
        """
        Returns the mutex used for thread safety.
        """
        if self._mutex is None:
            self._mutex = threading.Lock()
        return self._mutex

    @property
    def cached_reporter(self) -> CacheReporter:
        """
        Returns the cache reporter.
        """
        return self._cache_reporter

    @property
    def converter_container(self) -> ConvertersContainer:
        """
        Returns the converter container.
        """
        if self._converter_container is None:
            self._converter_container = ConvertersContainer()
        return self._converter_container

    @property
    def loaders_container(self) -> LoadersContainer:
        """
        Returns the loaders container.
        """
        if self._loaders_container is None:
            self._loaders_container = LoadersContainer()
        return self._loaders_container

    # -------------
    # Setters

    @cache_bank.setter
    def cache_bank(self, value: OrderedDict[str, OrderedDict[Tuple, Any]]) -> None:
        """
        Sets the cache bank.
        """
        try:
            if not isinstance(value, OrderedDict):
                raise TypeError("Cache bank must be an OrderedDict.")
            for key, val in value.items():
                if not isinstance(key, str):
                    raise TypeError("Cache bank keys must be strings.")
                if not isinstance(val, OrderedDict):
                    raise TypeError("Cache bank values must be OrderedDict.")
            self._cache_bank = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting cache bank: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting cache bank: {e}")

    @func_size_dict.setter
    def func_size_dict(self, value: Dict[str, CacheSize]) -> None:
        """
        Sets the function size dictionary.
        """
        try:
            if not isinstance(value, dict):
                raise TypeError("Function size dictionary must be a dictionary.")
            for key, val in value.items():
                if not isinstance(key, str):
                    raise TypeError("Function size dictionary keys must be strings.")
                if not isinstance(val, CacheSize):
                    raise TypeError("Function size dictionary values must be a CacheSize.")
            self._func_size_dict = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting function size dictionary: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting function size dictionary: {e}")

    @max_bank_size.setter
    def max_bank_size(self, value: int) -> None:
        """
        Sets the maximum size of the cache bank.
        """
        try:
            if not isinstance(value, int):
                raise TypeError("Maximum bank size must be an integer.")
            if value <= 0:
                raise ValueError("Maximum bank size must be greater than 0.")
            self._max_bank_size = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting max bank size: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting max bank size: {e}")
        
    @max_total_memory_size.setter
    def max_total_memory_size(self, value: int) -> None:
        """
        Sets the maximum total memory size of the cache bank.
        """
        try:
            if not isinstance(value, int):
                raise TypeError("Maximum total memory size must be an integer.")
            if value <= 0:
                raise ValueError("Maximum total memory size must be greater than 0.")
            if value <= sys.getsizeof(self):
                raise ValueError(f"Maximum total memory size {value} must be greater than the size of the cache bank - {sys.getsizeof(self)}.")
            if value < self.max_func_memory_size:
                raise ValueError(f"Maximum total memory size {value} must be greater than or equal to maximum function memory size - {self.max_func_memory_size}.")
            
            self._max_total_memory_size = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting max total memory size: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting max total memory size: {e}")

    @max_func_memory_size.setter
    def max_func_memory_size(self, value: int) -> None:
        """
        Sets the maximum size of a single function in the cache bank.
        """
        try:
            if not isinstance(value, int):
                raise TypeError("Maximum function memory size must be an integer.")
            if value <= 0:
                raise ValueError("Maximum function memory size must be greater than 0.")
            if value <= 128:
                raise ValueError("Maximum function memory size must be greater than 128.")
            if value > self.max_total_memory_size:
                raise ValueError(f"Maximum function memory size {value} must be less than or equal to maximum total memory size - {self.max_total_memory_size}.")
            
            self._max_func_memory_size = value

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting max function memory size: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting max function memory size: {e}")

    @max_file_size.setter
    def max_file_size(self, value: int) -> None:
        """
        Sets the maximum size of the cache bank file.
        """
        try:
            if not isinstance(value, int):
                raise TypeError("Maximum file size must be an integer.")
            if value <= 0:
                raise ValueError("Maximum file size must be greater than 0.")
            self._max_file_size = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting max file size: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting max file size: {e}")

    @lru.setter
    def lru(self, value: bool) -> None:
        """
        Sets the LRU (Least Recently Used) eviction policy.
        """
        try:
            if not isinstance(value, bool):
                raise TypeError("LRU must be a boolean.")
            self._lru = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting LRU: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting LRU: {e}")

    @filename.setter
    def filename(self, value: Union[str, Path]) -> None:
        """
        Sets the filename of the cache bank.
        """
        try:
            if not isinstance(value, (str, Path)):
                raise TypeError("Filename must be a string or Path object.")
            self._file_checker(value)
            self._filename = Path(value).resolve()
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting filename: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting filename: {e}")

    @cache_type.setter
    def cache_type(self, value: CacheType) -> None:
        """
        Sets the cache reporter.
        """
        try:
            if not isinstance(value, CacheType):
                raise TypeError("Cache reporter must be a CacheType object.")

            if value not in self.converter_container.get_keys():
                raise ValueError(f"Invalid cache type {value}. Must be one of: {', '.join(self._converter_container.get_keys())}")

            # Set cache type
            self._cache_type = value
            
            # Get the path
            path: Path = self.filename

            # Update the filename based on the cache type
            path: Path = self.filename
            self.filename = path.with_suffix(value)

            LOGGER.debug(f"Cache type set to {self._cache_type}.")
            LOGGER.debug(f"Cache bank file name set to {self.filename}.")

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting cache type: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting cache type: {e}")

    @converter_container.setter
    def converter_container(self, value: ConvertersContainer) -> None:
        """
        Sets the converter container.
        """
        try:
            if not isinstance(value, ConvertersContainer):
                raise TypeError("Converter container must be a ConvertersContainer object.")
            self._converter_container = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting converter container: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting converter container: {e}")

    @loaders_container.setter
    def loaders_container(self, value: LoadersContainer) -> None:
        """
        Sets the loaders container.
        """
        try:
            if not isinstance(value, LoadersContainer):
                raise TypeError("Loaders container must be a LoadersContainer object.")
            self._loaders_container = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting loaders container: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting loaders container: {e}")

    # -------------
    # Magic Methods

    def __str__(self) -> str:
        """
        Returns a string representation of the cache bank.
        """
        return f"CacheBank(max_bank_size={self.max_bank_size}, lru={self.lru}, cache_bank={self.cache_bank})"

    def __len__(self) -> int:
        """
        Returns the number of items in the cache bank.
        """
        return len(self.cache_bank)

    def __contains__(self, key: Any) -> bool:
        """
        Returns True if the key is in the cache bank, False otherwise.
        """
        return key in self.cache_bank
    
    def __getitem__(self, key: Any) -> Any:
        """
        Returns the value associated with the key in the cache bank.
        """
        try:
            if key in self.cache_bank:
                return self.cache_bank[key]
            else:
                raise KeyError(f"Key {key} not found in cache bank.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting item from cache bank: {e}")
            raise CacheBankMagicMethodError(f"Error '{e.__class__.__name__}' -> getting item from cache bank: {e}")
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Sets the value associated with the key in the cache bank.
        If the cache bank is full, it removes the least recently used item.
        """
        try:
            if self.lru:
                # If the cache bank is full, remove the least recently used item
                if len(self.cache_bank) >= self.max_bank_size:
                    self.cache_bank.popitem(last=False)
            
                # Add the new item to the cache bank
                self.cache_bank[key] = value
                # Move the item to the end of the OrderedDict to mark it as recently used
                self.cache_bank.move_to_end(key)
            else:
                # If the cache bank is full, remove the first item
                if len(self.cache_bank) >= self.max_bank_size:
                    self.cache_bank.popitem(last=True)
                
                # Add the new item to the cache bank
                self.cache_bank[key] = value
                # Move the item to the end of the OrderedDict to mark it as recently used
                self.cache_bank.move_to_end(key)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting item in cache bank: {e}")
            raise CacheBankMagicMethodError(f"Error '{e.__class__.__name__}' -> setting item in cache bank: {e}")

    def __delitem__(self, key: Any) -> None:
        """
        Deletes the item associated with the key in the cache bank.
        """
        try:
            if key in self.cache_bank:
                del self.cache_bank[key]
            else:
                raise KeyError(f"Key {key} not found in cache bank.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> deleting item from cache bank: {e}")
            raise CacheBankMagicMethodError(f"Error '{e.__class__.__name__}' -> deleting item from cache bank: {e}")

    # -------------
    # Methods

    def get(  
        self,
        func: Callable | partial, 
        args: Optional[Union[Tuple[Any, ...], List[Any]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        get
        ======
        Returns the value associated with the key in the cache bank.
        If the key is not found, it returns None.

        Arguments:
            func (Callable | partial) :
                The function to get the value for.
            args (Tuple[Any, ...] | List[Any]) :
                The arguments to the function.
            kwargs (Dict[str, Any]) :
                The keyword arguments to the function.
        """
        try:
            # Make the function hashable
            key: Tuple[Any, ...] = self.make_hashable(func, args, kwargs)

            # get func name
            func_name: str = key[0]

            if func_name not in self.cache_bank:
                LOGGER.debug(f"Function {func_name} not found in cache bank.")
                return None
            
            if key in self.cache_bank[func_name]:
                with self.mutex:
                    # Move the item to the end of the OrderedDict to mark it as recently used
                    self.cache_bank.move_to_end(func_name)
                    # Move result to the end of the OrderedDict to mark it as recently used
                    self.cache_bank[func_name].move_to_end(key)
                    # Increment the hit count
                    self._cache_reporter.set_hit(func_name)
                    # Return result
                    return self._cache_bank[func_name][key]
            else:
                LOGGER.debug(f"Key {key} not found in cache bank.")
                # Increment the miss count
                self._cache_reporter.set_miss(func_name)
                return None

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting item from cache bank: {e}")
            raise CacheBankGetError(f"Error '{e.__class__.__name__}' -> getting item from cache bank: {e}")
        
    def set(
        self, 
        func: Callable | partial, 
        args: Optional[Union[Tuple[Any, ...], List[Any]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None
    ) -> None:
        """
        set
        ======
        Sets the value associated with the key in the cache bank.
        If the cache bank is full, it removes the least recently used item.

        Arguments:
            func (Callable | partial) :
                The function to set the value for.
            args (Tuple[Any, ...] | List[Any]) :
                The arguments to the function.
            kwargs (Dict[str, Any]) :
                The keyword arguments to the function.
            result (Any) :
                The result of the function.
        """
        try:
            # Return if void
            if result is None:
                return
            
            # Make the function hashable
            tuple_func: Tuple[Any, ...] = self.make_hashable(func, args, kwargs)

            # get func name
            func_name: str = tuple_func[0]

            with self.mutex:

                # Add or update the cache entry
                if func_name not in self.cache_bank:
                    # Check LRU
                    self._lru_checker()
                    # Check and memory total LRU eviction
                    self._total_memory_checker()

                    self.cache_bank[func_name] = OrderedDict()
                    self._cache_reporter.add_func(func)
                    LOGGER.debug(f"Added {func_name} to cache bank.")
                
                # Check if the function have a specific mem constraint
                if self.func_size_dict.get(func_name, None) is not None:
                    # Check specific func size
                    self._func_specific_mem_checker(func_name)
                else:
                    # Check default func size
                    self._func_memory_checker()

                # Update the result in the cache
                self.cache_bank[func_name][tuple_func] = result
                # Move result to recently used
                self.cache_bank[func_name].move_to_end(tuple_func)
                # Move func to recently used
                self.cache_bank.move_to_end(func_name)
        
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting item in cache bank: {e}")
            raise CacheBankSetError(f"Error '{e.__class__.__name__}' -> setting item in cache bank: {e}")
    
    def clear(self) -> None:
        """
        clear
        ======
        Clears the cache bank.
        """
        try:
            with self.mutex:
                self.cache_bank.clear()
                self.cache_bank = OrderedDict()
                self._cache_reporter.clear()
                self._cache_reporter = CacheReporter()
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> clearing cache bank: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> clearing cache bank: {e}")
        
    def remove(self, func: str) -> None:
        """
        remove
        ======
        Removes the item associated with the key in the cache bank.
        """
        try:
            if func not in self.cache_bank:
                LOGGER.warning(f"Key {func} not found in cache bank.")
                return
            with self.mutex:
                del self[func]
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> removing item from cache bank: {e}")
            raise CacheBankMagicMethodError(f"Error '{e.__class__.__name__}' -> removing item from cache bank: {e}")
        
    def items(self) -> List[Tuple[Any, Any]]:
        """
        items
        ======
        Returns a list of tuples containing the key-value pairs in the cache bank.
        """
        try:
            return list(self.cache_bank.items())
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting items from cache bank: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> getting items from cache bank: {e}")
        
    def keys(self) -> List[Any]:
        """
        keys
        ======
        Returns a list of keys in the cache bank.
        """
        try:
            return list(self.cache_bank.keys())
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting keys from cache bank: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> getting keys from cache bank: {e}")
    
    def values(self) -> List[OrderedDict[Tuple, Any]]:
        """
        values
        ======
        Returns a list of values in the cache bank.
        """
        try:
            return list(self.cache_bank.values())
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting values from cache bank: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> getting values from cache bank: {e}")
        
    def set_log_level(self, log_level: int) -> None:
        """
        set_log_level
        =============
        Sets the log level for the cache bank.

        Arguments:
            log_level (int) :
                The log level to set.
        """
        try:
            LOGGER.setLevel(log_level)
            LOGGER.debug(f"Log level set to {log_level}.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting log level: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> setting log level: {e}")

    # -------------
    # Utils

    def is_full(self) -> bool:
        """
        is_full
        ======
        Returns True if the cache bank is full, False otherwise.
        """
        return len(self.cache_bank) >= self.max_bank_size           

    def is_empty(self) -> bool:
        """
        is_empty
        ======
        Returns True if the cache bank is empty, False otherwise.
        """
        return len(self.cache_bank) == 0
   
    def is_cache_report_empty(self) -> bool:
        """
        is_cache_report_empty
        =====================
        Returns True if the cache report is empty, False otherwise.
        """
        return self._cache_reporter.is_empty()

    # Reset Default

    def reset_default(self) -> None:
        """
        reset_default
        =============
        Resets the cache bank to its default state.
        """
        try:
            with self.mutex:
                self.max_bank_size = 100
                self.max_file_size = 100000
                self.lru = True

                self.cache_bank = OrderedDict()
                self._cache_reporter = CacheReporter()
                self._cache_type = CacheType.PICKLE
                self.filename = Path(__file__).parent.parent.parent.resolve().stem + ".pkl"
                self._mutex = None
                LOGGER.debug("Cache bank reset to default state.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> resetting cache bank: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> resetting cache bank: {e}")

    # Gets

    def get_cache_object_mem_size(self) -> int:
        """
        Returns the memory size of the cache object.
        """
        try:
            return sys.getsizeof(self.cache_bank)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting cache object memory size: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> getting cache object memory size: {e}")

    def get_func_object_mem_size(self, func:str) -> int:
        """
        Returns the memory size of the function object.
        """
        try:
            if not func:
                raise ValueError("Function name cannot be None or empty.")
            
            if not isinstance(func, str):
                raise TypeError("Function name must be a string.")

            if func not in self.cache_bank:
                raise KeyError(f"Function {func} not found in cache bank.")
            return sys.getsizeof(self.cache_bank[func])
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting function object memory size: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> getting function object memory size: {e}")

    def get_total_cache_size(self) -> int:
        """
        Returns the total size of the cache bank.
        """
        try:
            return len(self.cache_bank)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting total cache size: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> getting total cache size: {e}")


    # Prints

    def print(self) -> None:
        """
        print
        ======
        Prints the cache bank.
        """
        try:
            with self.mutex:
                string: str = "Cache Bank:\n"
                for key, value in self.cache_bank.items():
                    string += f"{key}: {value}\n"
                
            print(string)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing cache bank: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> printing cache bank: {e}")
        
    def print_full_report(self) -> None:
        """
        print_report
        ============
        Prints the report for the cache bank.
        """
        try:
            with self.mutex:
                string: str = "Cache Bank Report:\n"
                string += f"Max Bank Size: {self.max_bank_size}\n"
                string += f"LRU: {self.lru}\n"
                string += f"Cache Bank Length: {self.bank_length}\n"
                string += "Cache Bank:\n"
                for key, value in self.cache_bank.items():
                    string += f"\t{key}: {value}\n"
            
            print(string)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing cache bank report: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> printing cache bank report: {e}")

    def print_cache_report(self) -> None:
        """
        print_cache_report
        ==================
        Prints the cache report for the cache bank.
        """
        try:
            self._cache_reporter.print_report()
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing cache report: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> printing cache report: {e}")

    def print_func_stats(self, func: Callable) -> None:
        """
        print_func_stats
        ================
        Prints the statistics for a function in the cache bank.

        Arguments:
            func (Callable) :
                The function to print the statistics for.
        """
        try:
            if not callable(func):
                raise TypeError("Function must be callable.")
            if func.__name__ in self.cache_bank:
                self._cache_reporter.print_func_report(func)
            else:
                LOGGER.warning(f"Function {func.__name__} not found in cache bank.")
                print(f"Function {func.__name__} not found in cache bank.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing function statistics: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> printing function statistics: {e}")
        
    def print_full_func_stats(self) -> None:
        """
        print_full_func_stats
        ======================
        Prints the full statistics for all functions in the cache bank.
        """
        try:
            self._cache_reporter.print_full_func_reports()
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing full function statistics: {e}")
            raise CacheBankUtilsError(f"Error '{e.__class__.__name__}' -> printing full function statistics: {e}")

    # -------------
    # Adapter

    def make_hashable(
        self, 
        func: Callable | partial,
        args: Optional[Union[Tuple[Any, ...], List[Any]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any,...]:
        """
        make_hashable
        =============
        Converts the function and its arguments to a hashable tuple.

        Arguments:
            func (Callable | partial) :
                The function to convert to a hashable tuple.
            args (Tuple[Any, ...] | List[Any]) :
                The arguments to the function.
            kwargs (Dict[str, Any]) :
                The keyword arguments to the function.
        
        Returns:
            out (Tuple[Any, ...]) :
                A hashable tuple containing the function and its arguments.
        """
        try:
            if isinstance(func, partial):
                func_name: str = func.func.__name__
            elif callable(func):
                func_name: str = func.__name__
            else:
                raise TypeError("Function must be callable or partial.")
            
            args_list = []

            if args is not None:
                for arg in args:
                    if isinstance(arg, dict):
                        t_arg = tuple(sorted(arg.items()))
                        args_list.append(t_arg)
                    elif isinstance(arg, (list, tuple)):
                        args_list.append(tuple(arg))
                    else:
                        args_list.append(arg)

            # Convert args to a hashable tuple
            hash_args = tuple(args_list) if args_list else ()        
        
            if kwargs is not None and not isinstance(kwargs, dict):
                raise TypeError("Keyword arguments must be a dictionary.")
            
            hash_kwargs = tuple(sorted(kwargs.items())) if isinstance(kwargs, dict) else kwargs

            # Make the function hashable and return it

            if args and kwargs:
                return (func_name, hash_args, hash_kwargs)
            elif args:
                return (func_name, hash_args)
            elif kwargs:
                return (func_name, hash_kwargs)
            else:
                return (func_name,)
            
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> making hashable: {e}")
            raise CacheBankMakeHashableError(f"Error '{e.__class__.__name__}' -> making hashable: {e}")

    # -------------
    # Save/Load

    def save(self, filename: str | Path | None = None, level_compression: int = 1) -> None:
        """
        save
        ======
        Saves the cache bank to a file.

        Arguments:
            filename (str | Path | None) :
                The name of the file to save the cache bank to.
                If None, it will use the default filename.
            level_compression (int) :
                The level of compression to use when saving the cache bank.
                - Must be between 0 and 9
        Note:
        -------
        - If the file already exists, it will be overwritten.
        """
        # Make object from self
        io_buffer = io.BytesIO()
        try:
            if not isinstance(filename, (str, Path, type(None))):
                raise TypeError("Filename must be a string or Path object.")
            
            if filename is None:
                clean_filename = self.filename
                clean_filename = self._set_suffix(clean_filename)
            else:
                clean_filename: Path = Path(filename).resolve()
                clean_filename = self._set_suffix(clean_filename)

            # Check parent directory
            if not clean_filename.parent.exists():
                raise FileNotFoundError(
                    f"Parent directory {clean_filename.parent} does not exist."
                )
            
            # Check if file exists
            if clean_filename.exists():
                # Check if file is empty
                if os.path.getsize(clean_filename) == self.max_file_size:
                    os.remove(clean_filename)
                    LOGGER.warning(f"File {clean_filename} is full. Removing it.")
                else:
                    LOGGER.warning(f"File {clean_filename} already exists. Overwriting it.")
            else:
                LOGGER.info(f"File {clean_filename} does not exist. Creating it.")
                # Create the file
                clean_filename.parent.mkdir(parents=True, exist_ok=True)
                clean_filename.touch()

            # Save Handler
            save_func: Callable | None = self.converter_container[self.cache_type]
            if save_func is None:
                raise TypeError(f"Save function for cache type {self.cache_type} not found.")
            
            # Convert the cache bank to bytes
            if self.cache_type in [CacheType.ZLIB, CacheType.GZIP]:
                io_buffer.write(save_func(self.cache_bank, level_compression))
            else:
                io_buffer.write(save_func(self.cache_bank))

            # Check file size
            if len(io_buffer.getvalue()) > self.max_file_size:
                raise CacheBankSaveError(f"Serialized data size {len(io_buffer.getvalue())} exceeds max_file_size {self.max_file_size}")
            
            # Open the file in write mode
            with open(clean_filename, "wb") as f:
                # Check if file is writable
                if not f.writable():
                    raise IOError(f"File {clean_filename} is not writable.")
                
                with self.mutex:
                    # Save the cache bank to the file
                    f.write(io_buffer.getvalue())
                    LOGGER.info(f"Cache bank saved to {clean_filename}.")

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> saving cache bank: {e}")
            raise CacheBankSaveError(f"Error '{e.__class__.__name__}' -> saving cache bank: {e}")
        finally:
            io_buffer.close()

    def load(self, filename: str | Path | None = None) -> None:
        """
        load
        ======
        Loads the cache bank from a file.

        Attention:
        ----------
        Pickle data is unsafe, only load it from a trusted source.

        Arguments:
            filename (str | Path | None) :
                The name of the file to load the cache bank from.
                If None, it will use the default filename.
        
        """
        try:
            if not isinstance(filename, (str, Path, type(None))):
                raise TypeError("Filename must be a string or Path object.")
            
            if filename is None:
                clean_filename = self.filename
            else:
                clean_filename: Path = Path(filename).resolve()
                clean_filename = self._set_suffix(clean_filename)
            
            # Check if file exists
            if not clean_filename.exists():
                raise FileNotFoundError(f"File {clean_filename} does not exist.")
            
            # Get File Type
            file_type: CacheType | None = self._automatically_detect_file_type(str(clean_filename))

            # Check file type
            if file_type is None:
                LOGGER.warning(f"File type not recognized for {clean_filename}.")
                raise CacheBankLoadError(
                    f"File type not recognized for {clean_filename}."
                    f"\n Please use one of the following file types: {self.loaders_container.get_keys()}"
            )
            
            with self.mutex:
                with open(clean_filename, "rb") as f:
                    if not f.readable():
                        raise IOError(f"File {clean_filename} is not readable.")
                    
                    # Read the file
                    data: bytes = f.read(self.max_file_size)

                    # Get Bank
                    bank: OrderedDict = self._loader_handler(data, file_type)

                    # Update cache_bank
                    self.cache_bank = bank

                    LOGGER.info(f"Cache bank loaded from {clean_filename}.")

                self._lru_checker()
                self._total_memory_checker()
                self._func_memory_checker()

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}'-> loading cache bank: {e}")
            raise CacheBankLoadError(f"Error '{e.__class__.__name__}'-> loading cache bank: {e}")

    def remove_files(self) -> None:
        """
        remove_files
        ============
        Removes the cache bank files from standard path.

        Note:
        -------
        - The standard paths are:
            - ../cache/dump/cache_bank.pkl
            - ../cache/dump/cache_bank.zlib
            - ../cache/dump/cache_bank.gz
            - ../cache/dump/cache_bank.json
            - ../cache/dump/cache_bank.yaml
        """
        try:
            path_list: List[Path] = []

            for key in self.converter_container.get_keys():
                if key in [CacheType.PICKLE, CacheType.JSON, CacheType.YAML, CacheType.ZLIB, CacheType.GZIP]:
                    string: str = f"jr_cache_bank/cache/dump/cache_bank{key}"
                    path_list.append(Path(string))

            for path in path_list:
                if path.exists():
                    os.remove(path)
                    LOGGER.debug(f"Cache bank file {path} removed.")
                else:
                    LOGGER.debug(f"Cache bank file {path} does not exist, continuing ...")

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> removing cache bank files: {e}")
            raise CacheBankRemoveError(f"Error '{e.__class__.__name__}' -> removing cache bank files: {e}")

    # -------------
    # Async Save/Load

    async def async_save(self, filename: str | Path | None = None, level_compression: int = 1) -> None:
        """
        async_save
        ===========
        Asynchronously saves the cache bank to a file.

        Arguments:
            filename (str | Path | None) :
                The name of the file to save the cache bank to.
                If None, it will use the default filename.
            level_compression (int) :
                The level of compression to use when saving the cache bank.
                - Must be between 0 and 9
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.save, filename, level_compression)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> asynchronously saving cache bank: {e}")
            raise CacheBankAsyncSaveError(f"Error '{e.__class__.__name__}' -> asynchronously saving cache bank: {e}")

    async def async_load(self, filename: str | Path | None = None) -> None:
        """
        async_load
        ===========
        Asynchronously loads the cache bank from a file.

        Attention:
        ----------
        Pickle data is unsafe, only load it from a trusted source.

        Arguments:
            filename (str | Path | None) :
                The name of the file to load the cache bank from.
                If None, it will use the default filename.
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.load, filename)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> asynchronously loading cache bank: {e}")
            raise CacheBankAsyncLoadError(f"Error '{e.__class__.__name__}' -> asynchronously loading cache bank: {e}")

    # -------------
    # Helpers

    def _converter_handler(self, level_compression: int) -> bytes:
        """
        _converter_handler
        ==================
        Handles the conversion of the cache bank to bytes.
        
        Returns:
            bytes :
                The converted cache bank.
        """
        try:
            converter_func: Callable | None = self.converter_container[self.cache_type]
            if converter_func is None:
                raise ValueError(f"Converter function for cache type {self.cache_type} not found.")
            # Convert the cache bank to bytes
            if self.cache_type in [CacheType.ZLIB, CacheType.GZIP]:
                return converter_func(self.cache_bank, level_compression)
            else:
                return converter_func(self.cache_bank)
        except Exception as e:
            LOGGER.error(f"Error checking converter handler: {e}")
            raise e

    def _automatically_detect_file_type(self, filename: str) -> CacheType | None:
        """
        _automatically_detect_file_type
        ================================
        Automatically detects the file type based on the file extension.
        
        Arguments:
            filename (str) :
                The name of the file to check.
        
        Returns:
            CacheType :
                The detected file type.
            None :
                If the file type is not recognized.
        """
        try:
            if filename.endswith(".pkl") or filename.endswith(".pickle"):
                return CacheType.PICKLE
            elif filename.endswith(".zlib"):
                return CacheType.ZLIB
            elif filename.endswith(".gz"):
                return CacheType.GZIP
            elif filename.endswith(".json"):
                return CacheType.JSON
            elif filename.endswith(".yaml"):
                return CacheType.YAML
            else:
                return None
            
        except Exception as e:
            LOGGER.error(f"Error checking file type: {e}")
            raise e

    def _loader_handler(self, data: bytes, cache_type: CacheType) -> OrderedDict:
        """
        _loader_handler
        ===============
        Handles the loading of the cache bank from a file.

        Arguments:
            cache_type (CacheType) :
                The type of cache to load.
        
        Returns:
            out (OrderedDict) :
                The loaded cache bank.
        """
        try:
            loader_func: Callable | None = self.loaders_container[cache_type]
            if loader_func is None:
                raise ValueError(f"Loader function for cache type {cache_type} not found.")
            # Load the cache bank from the file
            bank: OrderedDict = loader_func(data)
            if not isinstance(bank, OrderedDict):
                raise TypeError(f"Cache bank must be an OrderedDict, got {type(bank)}.")
            return bank
        except Exception as e:
            LOGGER.error(f"Error checking loader handler: {e}")
            raise e

    def _file_checker(self, filename: str | Path) -> None:
        """
        file_checker
        ============
        Checks if the file follows the security rules.
        """
        try:
            if not isinstance(filename, (str, Path)):
                raise TypeError("Filename must be a string or Path object.")
            
            filename_str: str = str(filename) if isinstance(filename, Path) else filename
            
            if isinstance(filename_str, str):
                if len(filename_str) == 0:
                    raise ValueError("Filename cannot be empty.")
                if len(filename_str) > 255:
                    raise ValueError(f"Filename is too long, max length is 255 characters; got {len(filename_str)}")
            
            filename_path: Path = Path(filename_str).resolve()

            if not filename_path.parent.exists():
                raise FileNotFoundError(f"Parent directory {filename_path.parent} does not exist.")
            if not filename_path.parent.is_dir():
                raise NotADirectoryError(f"Parent directory {filename_path.parent} is not a directory.")

        except Exception as e:
            LOGGER.error(f"Error checking cache bank file: {e}")
            raise e

    def _lru_checker(self) -> None:
        """
        _lru_checker
        ============
        Checks if the cache bank is using LRU (Least Recently Used) eviction policy.
        
        If it is, it removes the least recently used item.
        Else, it removes the first item.
        """
        try:
            while len(self.cache_bank) >= self.max_bank_size:
            # If the cache bank is full, remove the least recently used item
                if self.lru:
                    self.cache_bank.popitem(last=False)
                else:
                    self.cache_bank.popitem(last=True)

        except Exception as e:
            LOGGER.error(f"Error checking LRU: {e}")
            raise e 
    
    def _func_specific_mem_checker(self, key: str) -> None:
        """
        _func_specific_mem_checker
        ==================
        Checks if the function is using more memory than specific maximum size.
        
        If it is, it removes the least recently used item.

        Arguments:
            key (str) :
                The key to check.
        """
        try:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            
            if self.func_size_dict.get(key) is None:
                return None

            if self.cache_bank.get(key) is None:
                return None

            if len(self.cache_bank[key]) == 0:
                return None
             
            func_size: int = self.func_size_dict[key]
            func_cached: int = self._memory_size_checker(self.cache_bank[key])
            
            if func_cached >= func_size:
                LOGGER.debug(
                    f"_func_specific_mem_checker - Function {key} size {func_cached} exceeds maximum size {func_size}. Trimming it."
                )

                while func_cached > func_size:
                    # If the cache bank is full, remove the least recently used item
                    if self.lru:
                        self.cache_bank[key].popitem(last=False)
                    else:
                        self.cache_bank[key].popitem(last=True)
                        
                    # Recalculate the size of the function for next iteration
                    func_cached: int = self._memory_size_checker(self.cache_bank[key])
                    LOGGER.debug(
                        f"Function {key} size after trimming: {func_cached}"
                    )

            return None

        except Exception as e:
            LOGGER.error(f"Error checking function specific memory: {e}")
            raise e

    def _total_memory_checker(self) ->None:
        """
        _total_memory_checker
        =====================
        Checks if the total memory size of the cache bank is greater than the maximum size.
        
        If it is, it removes the least recently used item.
        """
        try:
            total_cache_size: int = self._memory_size_checker(self.cache_bank)

            while total_cache_size >= self.max_total_memory_size:
                LOGGER.debug(f"_total_memory_checker - Total cache size: {total_cache_size}, Max total memory size: {self.max_total_memory_size}, removing least recently used item.")

                # If the cache bank is full, remove the least recently used item
                if self.lru:
                    self.cache_bank.popitem(last=False)
                else:
                    self.cache_bank.popitem(last=True)
                total_cache_size = self._memory_size_checker(self.cache_bank)

        except Exception as e:
            LOGGER.error(f"Error checking total memory size: {e}")
            raise e

    def _func_memory_checker(self) -> None:
        """
        _func_memory_checker
        ====================
        Checks if the memory size of the function is greater than the default maximum size.
        
        If it is, it removes the least recently used item.
        """
        try:
            for func in self.cache_bank:
                func_size: int = self._memory_size_checker(self.cache_bank[func])

                if func_size >= self.max_func_memory_size:
                    LOGGER.debug(
                        f"_func_memory_checker - Function {func} size {func_size} exceeds maximum size {self.max_func_memory_size}. Trimming it."
                    )
                    while func_size > self.max_func_memory_size:
                        # If the cache bank is full, remove the least recently used item
                        if self.lru:
                            self.cache_bank[func].popitem(last=False)
                        else:
                            self.cache_bank[func].popitem(last=True)
                        func_size = self._memory_size_checker(self.cache_bank[func])
                        
        except Exception as e:
            LOGGER.error(f"Error checking function memory size: {e}")
            raise e

    def _set_prefix(self) -> Path:
        """
        _set_prefix
        ===========
        Sets the prefix of the file to the name of the module.
        
        Returns:
            Path :
                The path to the file with the correct prefix.
        """
        string_prefix: str = Path(__file__).parent.parent.parent.resolve().stem

        for key in self.converter_container.get_keys():
            if self.cache_type == key:
                string_prefix = string_prefix + key
                break
        return Path(string_prefix).resolve()

    def _set_suffix(self, path: Path) -> Path:
        """
        _set_suffix
        ===========
        Sets the suffix of the file to .pkl or .pickle.

        Arguments:
            path (Path) :
                The path to the file.
        
        Returns:
            Path :
                The path to the file with the correct suffix.
        """
        if path.suffix in self.converter_container.get_keys():
            return path
        else:
            for suffix in self.converter_container.get_keys():
                if self.cache_type == suffix:
                    path = path.with_suffix(suffix)
                    break
        return path

    def _memory_size_checker(self, obj, seen=None) -> int:
        if seen is None:
            seen = set()
        obj_id = id(obj)
        # Check if the object has already been seen to avoid infinite recursion
        if obj_id in seen:
            return 0
        # If not add obj to set
        seen.add(obj_id)
        # Get the size of the object
        size = sys.getsizeof(obj)
        # For nested data
        if isinstance(obj, dict):
            # Get values size
            size += sum(self._memory_size_checker(v, seen) for v in obj.values())
            # Get keys size
            size += sum(self._memory_size_checker(k, seen) for k in obj.keys())
        
        # If the object is a list, tuple, or set
        elif isinstance(obj, (list, tuple, set)):
            # Sum every element
            size += sum(self._memory_size_checker(i, seen) for i in obj)
        return size


    @staticmethod
    def _dict_sanitizer(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        _dict_sanitizer
        ===============
        Sanitizes the dictionary to remove any non-serializable values.
        
        Arguments:
            data (Dict[str, Any]) :
                The dictionary to sanitize.
        
        Returns:
            Dict[str, Any] :
                The sanitized dictionary.
        """
        try:
            if not isinstance(data, dict):
                raise TypeError("Data must be a dictionary.")

            if "cache_bank" in data:
                data["cache_bank"] =  OrderedDict(data["cache_bank"])
            if "cache_type" in data:
                data["cache_type"] = CacheType(data["cache_type"])
            if  "max_total_memory_size" in data:
                data["max_total_memory_size"] = CacheSize(data["max_total_memory_size"])
            if "max_func_memory_size" in data:
                data["max_func_memory_size"] = CacheSize(data["max_func_memory_size"])
            return data

        except Exception as e:
            LOGGER.error(f"Error sanitizing dictionary: {e}")
            raise e

    # -------------
    # wrappers

    def wrapper(self, max_size: Optional[CacheSize] = None) -> Callable:
        """
        wrapper
        ========
        Creates a wrapper for the function.
        - If the function is already in the cache bank, it returns the result from the cache bank.
        - If the function is not in the cache bank, it calls the function and sets the result in the cache bank.

        Arguments:
            max_size (CacheSize) :
                The maximum size of the function in the cache bank.
                If None, it will use the default size.

        Example:
        ```python
            # Make a cache bank
            cache = CacheBank()

            # Wrap the function
            @cache.wrapper()
            def some_function(x, y):
                return x + y

            # Wrap with specific memory restriction
            @cache.wrapper(max_size=CacheSize.E_128KB)
            def some_function(x, y):
                return x + y
        ```
        """
        try:
            def inner(func: Callable | partial) -> Callable:
                @wraps(func)
                def wrapper(*args, **kwargs):
                    # Check if the function callable or partial
                    if not callable(func) and not isinstance(func, partial):
                        raise TypeError("Function must be callable or partial.")

                    # Get name
                    if isinstance(func, partial):
                        func_name: str = func.func.__name__
                    else:
                        func_name: str = func.__name__

                    # Set settings func max size
                    if max_size is not None:
                        if not isinstance(max_size, CacheSize):
                            raise TypeError("Max size must be an CacheSize.")
                        self.func_size_dict[func_name] = max_size

                    # Check if the function is already in the cache bank
                    if func_name in self.cache_bank:
                        # If it is, get the result from the cache bank
                        result = self.get(func, args, kwargs)
                        # Will return None if no result is found
                        if result is not None:
                            return result
                        
                    # If it is not, call the function and set the result in the cache bank
                    result = func(*args, **kwargs)
                    self.set(func, args, kwargs, result)

                    return result
                return wrapper
            return inner
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> creating wrapper: {e}")
            raise e
    
    def async_wrapper(self, max_size: Optional[CacheSize] = None):
        """
        async_wrapper
        =============
        Creates an async wrapper for the function.
        - If the function is already in the cache bank, it returns the result from the cache bank.
        - If the function is not in the cache bank, it calls the function and sets the result in the cache bank.

        Arguments:
            max_size (CacheSize) :
                The maximum size of the function in the cache bank.
                If None, it will use the default size.

        Example:
        ```python
            # Make a cache bank
            cache = CacheBank()

            # Wrap the function
            @cache.async_wrapper()
            async def some_function(x, y):
                return x + y
            
            # Wrap with specific memory restriction
            @cache.async_wrapper(max_size=CacheSize.E_128KB)
            async def some_function(x, y):
                return x + y
        ```
        """
        try:
            def inner(func):
                # Check if the function is a coroutine function
                if not asyncio.iscoroutinefunction(func):
                    raise TypeError("Function must be a coroutine function.")
                    
                @wraps(func)
                async def wrapper(*args, **kwargs):
                    
                    # Get name
                    func_name: str = func.__name__
                    if isinstance(func, partial):
                        func_name: str = func.func.__name__

                    # Set settings func max size
                    if max_size is not None:
                        if not isinstance(max_size, CacheSize):
                            raise TypeError("Max size must be an CacheSize.")
                        self.func_size_dict[func_name] = max_size

                    # Check if the function is already in the cache bank
                    if func_name in self.cache_bank:
                        # If it is, get the result from the cache bank
                        result = self.get(func, args, kwargs)
                        if result is not None:
                            return result
                        
                    # If it is not, call the function and set the result in the cache bank
                    result = await func(*args, **kwargs)
                    self.set(func, args, kwargs, result)
                    
                    return result
                return wrapper
            return inner
        
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> creating wrapper: {e}")
            raise e

    def __call__(
        self, 
        func: Callable | partial,
        max_size: Optional[CacheSize] = None,
    )-> Callable:
        """
        __call__
        ========
        Calls the wrapper function.
        - If the function is already in the cache bank, it returns the result from the cache bank.

        Arguments:
            func (Callable | partial) :
                The function to wrap.
            max_size (CacheSize) :
                The maximum size of the function in the cache bank.
                If None, it will use the default size.
        
        Returns:
            Callable :
                The wrapped function.

        Example:
            ```python
                my_cache_bank = CacheBank()
                # This will cache the func and return the result
                wrapped_func = my_cache_bank(my_function)
                # Cache with specific memory restriction
                wrapped_func = my_cache_bank(my_function, max_size=CacheSize.E_128KB)
            ```

        """
        try:
            if not callable(func) and not isinstance(func, partial):
                raise TypeError("Function must be callable or partial.")

            # Get the function name
            func_name = func.func.__name__ if isinstance(func, partial) else func.__name__

            # Update func_size_dict if max_size is provided
            if max_size is not None:
                if not isinstance(max_size, CacheSize):
                    raise TypeError("Max size must be a CacheSize.")
                self.func_size_dict[func_name] = max_size

            if asyncio.iscoroutinefunction(func):
                return self.async_wrapper(max_size)(func)
            else:
                if not callable(func) and not isinstance(func, partial):
                    raise TypeError("Function must be callable or partial.")
                return self.wrapper(max_size)(func)
        except Exception as e:
            LOGGER.error(f"Error calling wrapper: {e}")
            raise e

    # -------------
    # Config

    def config_from_dict(self, data: Dict[str, Any]) -> None:
        """
        config_from_dict
        ================
        Configures the cache bank from a dictionary.

        Arguments:
            data (Dict[str, Any]) :
                The dictionary to configure the cache bank from.
        
        """
        try:
            if not isinstance(data, dict):
                raise TypeError("Data must be a dictionary.")
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    LOGGER.warning(f"Key {key} not found in cache bank.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> configuring cache bank from dict: {e}")
            raise CacheBankConfigError(f"Error '{e.__class__.__name__}' -> configuring cache bank from dict: {e}")

    def config_from_json(self, data: bytes) -> None:
        """
        config_from_json
        ================
        Configures the cache bank from a JSON file.

        Arguments:
            data (bytes) :
                The JSON file to configure the cache bank from.
        
        """
        try:
            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            # Load the JSON file
            data_dict: Dict[str, Any] = json.loads(data)
            clean_dict: Dict[str, Any] = CacheBank._dict_sanitizer(data_dict)
            
            self.config_from_dict(clean_dict)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> configuring cache bank from JSON: {e}")
            raise CacheBankConfigError(f"Error '{e.__class__.__name__}' -> configuring cache bank from JSON: {e}")
    
    # Static

    @staticmethod
    def static_config_from_dict(data: Dict[str, Any]) -> 'CacheBank':
        """
        static_config_from_dict
        ========================
        Configures the cache bank from a dictionary.

        Arguments:
            data (Dict[str, Any]) :
                The dictionary to configure the cache bank from.
        
        Returns:
            CacheBank :
                The configured cache bank.
        
        """
        try:
            if not isinstance(data, dict):
                raise TypeError("Data must be a dictionary.")
            return CacheBank(**data)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> configuring cache bank from dict: {e}")
            raise CacheBankConfigError(f"Error '{e.__class__.__name__}' -> configuring cache bank from dict: {e}")
        
    @staticmethod
    def static_config_from_json(data: bytes) -> 'CacheBank':
        """
        static_config_from_json
        ========================
        Configures the cache bank from a JSON file.

        Arguments:
            data (bytes) :
                The JSON file to configure the cache bank from.
        
        Returns:
            CacheBank :
                The configured cache bank.
        
        """
        try:
            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            # Load the JSON file
            data_dict: Dict[str, Any] = json.loads(data)
            clean_dict: Dict[str, Any] = CacheBank._dict_sanitizer(data_dict)

            return CacheBank(**clean_dict)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> configuring cache bank from JSON: {e}")
            raise CacheBankConfigError(f"Error '{e.__class__.__name__}' -> configuring cache bank from JSON: {e}")
    

# -------------------------------------------------------------------------------------------------