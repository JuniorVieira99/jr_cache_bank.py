# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import gzip
import json
import yaml
import zlib
import logging
import pickle

from collections import OrderedDict
from ast import literal_eval
from typing import Any, Callable, Dict, Optional, Tuple

from jr_cache_bank.config.setup_logger import setup_logger
from jr_cache_bank.cache.cache_enums import CacheType

# -------------------------------------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------------------------------------

try:
    LOGGER: logging.Logger = setup_logger()
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

class LoadersContainer:
    """
    LoadersContainer
    ============
    The LoadersContainer class is a container for cache loaders. It provides methods to load cache data
    from various formats such as pickle, zlib, gzip, json, and yaml.

    Attention
    ----------
    Pickle data is unsafe to load, only use it if you trust the source of the data.

    Attributes:
        loaders (Dict[str, Callable]):
            A dictionary mapping cache types to their corresponding loader functions.

    Methods
    --------
        ### add_loader(key: str, loader: Callable) -> None:
            Adds a loader to the LoadersContainer.
        ### get_loader(key: str) -> Optional[Callable]:
            Gets a loader by key.
        ### remove_loader(key: str) -> None:
            Removes a loader from the LoadersContainer.
        ### cleanup() -> None:
            Cleans up the LoadersContainer.
        
    Default Loaders:
    -----------------
        - CacheType.PICKLE : Loads the cache bank from a pickle object.
        - CacheType.ZLIB : Loads the cache bank from a zlib object.
        - CacheType.GZIP : Loads the cache bank from a gzip object.
        - CacheType.JSON : Loads the cache bank from a json object.
        - CacheType.YAML : Loads the cache bank from a yaml object.

    """

    # ------------
    # Slots

    __slots__ = (
        "_loaders"
    )

    # ------------
    # Attributes

    _loaders: Dict[str, Callable]

    # ------------
    # Constructor
    def __init__(self):
        """
        Initialize the ConvertersContainer.
        """
        self._loaders: Dict[str, Callable] = self._default_map_loaders()

    # ------------
    # Magic Methods

    def __str__(self) -> str:
        """
        Return a string representation of the ConvertersContainer.
        """
        return f"CacheLoadComp(loaders={self.loaders})"
    
    def __len__(self) -> int:
        """
        Return the number of loaders in the ConvertersContainer.
        """
        return len(self._loaders)
    
    def __getitem__(self, key: str) -> Optional[Callable]:
        """
        Get a loader by key.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        if not key:
            raise ValueError("Key cannot be empty")
        
        if key in self._loaders:
            return self._loaders[key]
        else:
            LOGGER.warning(f"Loader '{key}' not found in loaders.")
            return None
        
    def __setitem__(self, key: str, value: Callable) -> None:
        """
        Set a loader by key.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        if not key:
            raise ValueError("Key cannot be empty")
        
        if not callable(value):
            raise TypeError(f"Value must be callable, got {type(value)}")
        
        self._loaders[key] = value

    def __delitem__(self, key: str) -> None:
        """
        Delete a loader by key.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        if not key:
            raise ValueError("Key cannot be empty")
        
        if key in self._loaders:
            del self._loaders[key]
        else:
            LOGGER.warning(f"Loader '{key}' not found in loaders.")

    # ------------
    # Properties

    @property
    def loaders(self) -> Dict[str, Callable]:
        """
        Get the loaders.
        """
        return self._loaders
    
    # ------------
    # Setters
    
    @loaders.setter
    def loaders(self, value: Dict[str, Callable]) -> None:
        """
        Set the loaders.
        """
        if not isinstance(value, dict):
            raise TypeError(f"Value must be a dictionary, got {type(value)}")
        
        for key, val in value.items():
            if not isinstance(key, str):
                raise TypeError(f"Key must be a string, got {type(key)}")
            if not key:
                raise ValueError("Key cannot be empty")
            
            if not callable(val):
                raise TypeError(f"Value must be callable, got {type(val)}")
        
        self._loaders = value

    # ------------
    # Methods

    def add_loader(self, key: str, loader: Callable) -> None:
        """
        Add a loader to the ConvertersContainer.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        if not key:
            raise ValueError("Key cannot be empty")
        
        if not callable(loader):
            raise TypeError(f"Loader must be callable, got {type(loader)}")
        
        self._loaders[key] = loader

    def get_loader(self, key: str) -> Optional[Callable]:
        """
        Get a loader by key.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        if not key:
            raise ValueError("Key cannot be empty")
        
        if key in self._loaders:
            return self._loaders[key]
        else:
            LOGGER.warning(f"Loader '{key}' not found in loaders.")
            raise KeyError(f"Loader '{key}' not found in loaders.")

    def remove_loader(self, key: str) -> None:
        """
        Remove a loader from the ConvertersContainer.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        if not key:
            raise ValueError("Key cannot be empty")
        
        if key in self._loaders:
            if key not in [CacheType.PICKLE, CacheType.ZLIB, CacheType.GZIP, CacheType.JSON, CacheType.YAML]:
                del self._loaders[key]
            else:
                LOGGER.warning(f"Loader '{key}' is a default loader and cannot be removed.")
        else:
            LOGGER.warning(f"Loader '{key}' not found in loaders.")

    def cleanup(self) -> None:
        """
        Cleanup the ConvertersContainer.
        """
        default_keys = {CacheType.PICKLE, CacheType.ZLIB, CacheType.GZIP, CacheType.JSON, CacheType.YAML}
        keys_to_remove = [k for k in self._loaders.keys() if k not in default_keys]
        for key in keys_to_remove:
            del self._loaders[key]

    def get_keys(self) -> list:
        """
        Get the keys of the loaders.
        """
        return list(self.loaders.keys())

    # ------------
    # Helpers

    def _reconstruct_key(self, func_name: str, args: Tuple, kwargs: Dict) -> Tuple:
        if not args and not kwargs:
            return (func_name,)
        elif args and not kwargs:
            return (func_name, args)
        elif not args and kwargs:
            return (func_name, kwargs)
        else:
            return (func_name, args, kwargs)

    def _deserialization(
        self, 
        data: OrderedDict[str, OrderedDict[str, Any]]
    ) -> OrderedDict[str, OrderedDict[Tuple[str, ...], Any]]:
        """
        _deserialization
        ================
        Deserializes the cache bank data.
        This method converts the stringified keys back to tuples.

        Arguments:
            data (OrderedDict[str, OrderedDict[str, Any]]): 
                The data to deserialize.

        Returns:
            out (OrderedDict[str, OrderedDict[Tuple[str, ...], Any]]): 
                The deserialized data.
        """
        # Convert stringified keys back to tuples
        cache_bank = OrderedDict()
        
        for func_name, ord_dict in data.items():
            cache_bank[func_name] = OrderedDict()
            # key is a stringified tuple / value is the cached value
            for key, value in ord_dict.items():
                if not isinstance(key, str):
                    raise TypeError(f"Keys of cached function must be a string, got {type(key)}")

                # Parse the stringified tuple
                try:
                    parsed = literal_eval(key)
                except (ValueError, SyntaxError) as e:
                    LOGGER.error(f"Error '{e.__class__.__name__}' -> Failed to parse key '{key}': {e}")
                    continue

                if not isinstance(parsed, tuple):
                    raise TypeError(f"Parsed key must be a tuple, got {type(parsed)}")

                # Get each part of the parsed tuple
                parsed_func_name: str = parsed[0]
                args: Tuple[Any, ...] = ()
                kwargs: Dict[str, Any] = {}
                
                if len(parsed) == 2:
                    args = parsed[1] if isinstance(parsed[1], tuple) else (parsed[1],)
                elif len(parsed) == 3:
                    args = parsed[1] if isinstance(parsed[1], tuple) else (parsed[1],)
                    kwargs = parsed[2] if isinstance(parsed[2], dict) else {}
                
                # Make key a tuple
                new_key = self._reconstruct_key(parsed_func_name, args, kwargs)
                # Update the key in the cache bank
                cache_bank[func_name][new_key] = value
        
        return cache_bank

    # ------------
    # Loaders

    def _load_pickle(self, data: bytes) -> OrderedDict:
        """
        _load_pickle
        ============
        Loads the cache bank from a pickle object.

        Arguments:
            data (bytes): 
                The data to load.

        Returns:
            out (OrderedDict) : 
                The loaded data.
        """
        try:
            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            # Unpickle the data
            out = pickle.loads(data)
            # Check if the data is an OrderedDict
            if not isinstance(out, OrderedDict):
                raise TypeError(f"Cache bank must be an OrderedDict, got {type(out)}.")
            return out
        except Exception as e:
            LOGGER.error(f"Error loading pickle: {e}")
            raise e
    
    def _load_zlib(self, data: bytes) -> OrderedDict:
        """
        _load_zlib
        ==========
        Loads the cache bank from a zlib object.

        Arguments:
            data (bytes): 
                The data to load.

        Returns:
            OrderedDict: 
                The loaded data.
        """
        try:
            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            # Uncompress the data
            out: OrderedDict = pickle.loads(zlib.decompress(data))
            # Check if the output is an OrderedDict
            if not isinstance(out, OrderedDict):
                raise TypeError(f"Cache bank must be an OrderedDict, got {type(out)}.")
            return out
        except Exception as e:
            LOGGER.error(f"Error loading zlib: {e}")
            raise e

    def _load_gzip(self, data: bytes) -> OrderedDict:
        """
        _load_gzip
        ==========
        Loads the cache bank from a gzip object.

        Arguments:
            data (bytes): 
                The data to load.

        Returns:
            OrderedDict: 
                The loaded data.
        """
        try:
            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            out: OrderedDict = pickle.loads(gzip.decompress(data))
            # Check if the output is an OrderedDict
            if not isinstance(out, OrderedDict):
                raise TypeError(f"Cache bank must be an OrderedDict, got {type(out)}.")
            return out
        except Exception as e:
            LOGGER.error(f"Error loading gzip: {e}")
            raise e

    def _load_json(self, data: bytes) -> OrderedDict:
        """
        _load_json
        ==========
        Loads the cache bank from a json object.

        Arguments:
            data (bytes): 
                The data to load.

        Returns:
            OrderedDict: 
                The loaded data.
        """
        try:
            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            
            # Decode bytes to string
            json_str = data.decode("utf-8")

            # Load JSON data with custom decoder
            loaded_data: OrderedDict = json.loads(
                json_str,
                object_pairs_hook=OrderedDict
            )

            # Convert stringified keys back to tuples
            cache_bank = self._deserialization(loaded_data)

            # Check if the output is an OrderedDict
            if not isinstance(cache_bank, OrderedDict):
                raise TypeError(f"Cache bank must be an OrderedDict, got {type(cache_bank)}.")
            
            return cache_bank
        except Exception as e:
            LOGGER.error(f"Error loading json: {e}")
            raise e
        
    def _load_yaml(self, data: bytes) -> OrderedDict:
        """
        _load_yaml
        ==========
        Loads the cache bank from a yaml object.

        Arguments:
            data (bytes): 
                The data to load.

        Returns:
            OrderedDict: 
                The loaded data.
        """
        def ordered_dict_constructor(loader, node):
            """
            Custom constructor for OrderedDict.
            """
            return OrderedDict(loader.construct_pairs(node))
    
        try:
            # Add the custom constructor to the yaml loader
            yaml.add_constructor(
                "tag:yaml.org,2002:python/object/apply:collections.OrderedDict",
                ordered_dict_constructor,
                Loader=yaml.FullLoader
            )

            if not isinstance(data, bytes):
                raise TypeError("Data must be a bytes object.")
            
            # Uncompress the data
            loaded_data: OrderedDict = yaml.load(data, Loader=yaml.FullLoader)

            # Deserialize the data
            cache_bank = self._deserialization(loaded_data)

            # Check if the output is an OrderedDict
            if not isinstance(cache_bank, OrderedDict):
                raise TypeError(f"Cache bank must be an OrderedDict, got {type(cache_bank)}.")
            
            return cache_bank
        except Exception as e:
            LOGGER.error(f"Error loading yaml: {e}")
            raise e

    def _default_map_loaders(self) -> Dict[str, Callable]:
        """
        _load_map
        =========
        Maps the cache type to the corresponding loader function.

        Map:
        -------
        ```python
        map = {
            CacheType.PICKLE: self._load_pickle,
            CacheType.ZLIB: self._load_zlib,
            CacheType.GZIP: self._load_gzip,
            CacheType.JSON: self._load_json,
            CacheType.YAML: self._load_yaml
        }
        ```
        """
        return {
            CacheType.PICKLE: self._load_pickle,
            CacheType.ZLIB: self._load_zlib,
            CacheType.GZIP: self._load_gzip,
            CacheType.JSON: self._load_json,
            CacheType.YAML: self._load_yaml
        }

