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

class ConvertersContainer:
    """
    ConvertersContainer
    ==============
    A container for the different converters used in the cache bank.
    The converters are used to convert the cache bank to different formats.

    Attributes:
        converters (Dict[str, Callable]) :
            A dictionary of the different converters used in the cache bank.
            The keys are the names of the converters and the values are the converter functions.

    Methods:
    -----------------
        ### add_converter(name: str, converter: Callable) :
            Add a converter to the container.
        ### get_converter(name: str) -> Optional[Callable] :
            Get a converter from the container.
        ### remove_converter(name: str) :
            Remove a converter from the container.
        ### clear_converters() :
            Clear all non-default converters from the container.

    Default Converters:
    -----------------
        - CacheType.PICKLE : Converts the cache bank to a pickle object.
        - CacheType.ZLIB : Converts the cache bank to a zlib object.
        - CacheType.GZIP : Converts the cache bank to a gzip object.
        - CacheType.JSON : Converts the cache bank to a json object.
        - CacheType.YAML : Converts the cache bank to a yaml object.
    """

    # ------------
    # Slots

    __slots__ = (
        "_converters"
    )

    # ------------
    # Attributes

    _converters: Dict[str, Callable]

    # ------------
    # Constructor
    def __init__(self):
        """
        Initialize the ConvertersContainer.
        """
        self._converters: Dict[str, Callable] = self._default_map_converters()

    # ------------
    # Magic Methods

    def __str__(self) -> str:
        """
        Get the string representation of the ConvertersContainer.

        Returns:
            out (str): The string representation of the ConvertersContainer.
        """
        return f"ConvertersContainer({self.converters})"
    
    def __len__(self) -> int:
        """
        Get the length of the ConvertersContainer.

        Returns:
            out (int): The number of converters in the container.
        """
        return len(self.converters)

    def __getitem__(self, name: str) -> Optional[Callable]:
        """
        Get the converter from the ConvertersContainer.

        Args:
            name (str): The name of the converter.

        Returns:
            out (Optional[Callable]): The converter function, or None if not found.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        
        return self.converters.get(name)
    
    def __setitem__(self, name: str, converter: Callable):
        """
        Set the converter in the ConvertersContainer.

        Args:
            name (str): The name of the converter.
            converter (Callable): The converter function.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        if not callable(converter):
            raise TypeError("Converter must be callable.")
        
        self.converters[name] = converter
    
    def __delitem__(self, name: str):
        """
        Delete the converter from the ConvertersContainer.

        Args:
            name (str): The name of the converter.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        
        if name in self.converters:
            del self.converters[name]
        else:
            raise KeyError(f"Converter '{name}' not found in ConvertersContainer.")

    # ------------
    # Properties

    @property
    def converters(self) -> Dict[str, Callable]:
        """
        Get the converters in the container.

        Returns:
            out (Dict[str, Callable]): The converters in the container.
        """
        return self._converters
    
    # ------------
    # Setters

    @converters.setter
    def converters(self, value: Dict[str, Callable]):
        """
        Set the converters in the container.

        Args:
            value (Dict[str, Callable]): The converters to set.
        """
        if not isinstance(value, dict):
            raise TypeError("Converters must be a dictionary.")
        self._converters = value

    # ------------
    # Methods

    def add_converter(self, name: str, converter: Callable):
        """
        Add a converter to the container.

        Args:
            name (str): The name of the converter.
            converter (Callable): The converter function.
        """
        if not callable(converter):
            raise TypeError("Converter must be callable.")
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        self.converters[name] = converter

    def get_converter(self, name: str) -> Optional[Callable]:
        """
        Get a converter from the container.

        Args:
            name (str): The name of the converter.

        Returns:
            Optional[Callable]: The converter function, or None if not found.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        
        return self.converters.get(name)    
    
    def remove_converter(self, name: str):
        """
        Remove a converter from the container.

        Args:
            name (str): The name of the converter.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        
        if name in [CacheType.PICKLE, CacheType.ZLIB, CacheType.GZIP]:
            raise ValueError("Cannot remove default converters.")
        
        if name in self.converters:
            del self.converters[name]

    def clear_converters(self):
        """
        Clear all non-default converters from the container.
        """
        for key, _ in self.converters.items():
            if key not in [CacheType.PICKLE, CacheType.ZLIB, CacheType.GZIP, CacheType.JSON, CacheType.YAML]:
                del self.converters[key]

        # Converters

    def get_keys(self) -> list:
        """
        get_keys
        ========
        Get the keys of the converters in the container.

        Returns:
            out (list) :
                The keys of the converters in the container.
        """
        return list(self.converters.keys())

    # ------------
    # Helpers

    def _convert_tuple_key_to_string(
        self,
        cache_bank: OrderedDict[str, OrderedDict[Tuple, Any]]
    ) -> OrderedDict[str, OrderedDict[str, Any]]:
        """
        _convert_tuple_key_to_string
        ============================
        Converts the keys of the cache bank from tuples to strings.

        Arguments:
            cache_bank (OrderedDict) :
                The cache bank to convert.

        Returns:
            out (OrderedDict) :
                The converted cache bank.
        """
        serializable_cache_bank = OrderedDict()
        for func_name, ord_dict in cache_bank.items():
            serializable_cache_bank[func_name] = OrderedDict()
            for key, value in ord_dict.items():
                str_key = str(key)  # Convert tuple key to string
                serializable_cache_bank[func_name][str_key] = value 
                    
        return serializable_cache_bank   

    # ------------
    # Converters

    def _make_pickle(self, cache_bank: OrderedDict) -> bytes:
        """
        _make_pickle
        ============
        Converts the cache bank to a pickle object.

        Arguments:
            cache_bank (OrderedDict) :
                The cache bank to convert.
        """
        try:
            pickle_data: bytes = pickle.dumps(cache_bank)
            return pickle_data
        except Exception as e:
            LOGGER.error(f"Error making pickle: {e}")
            raise e
    
    def _make_zlib(self, cache_bank: OrderedDict, level_compression: int = 1) -> bytes:
        """
        _make_zlib
        ==========
        Converts the cache bank to a zlib object.

        Arguments:
            cache_bank (OrderedDict) :
                The cache bank to convert.
            level_compression (int) :
                The level of compression to use.
                - Default is 1.
        """
        try:
            # Check level of compression
            if not isinstance(level_compression, int):
                raise TypeError("Level of compression must be an integer.")
            if level_compression < 0 or level_compression > 9:
                raise ValueError("Level of compression must be between 0 and 9.")
            
            zlib_data: bytes = zlib.compress(pickle.dumps(cache_bank), level_compression)
            # Check if data is bytes
            if not isinstance(zlib_data, bytes):
                raise TypeError("Compressed data must result in a bytes object.")
            
            return zlib_data
        except Exception as e:
            LOGGER.error(f"Error making zlib: {e}")
            raise e

    def _make_gzip(self, cache_bank: OrderedDict, level_compression: int = 1) -> bytes:
        """
        _make_gzip
        ==========
        Converts the cache bank to a gzip object.

        Arguments:
            cache_bank (OrderedDict) :
                The cache bank to convert.
            level_compression (int) :
                The level of compression to use.
                - Default is 1.
        """
        try:
            # Check level of compression
            if not isinstance(level_compression, int):
                raise TypeError("Level of compression must be an integer.")
            if level_compression < 0 or level_compression > 9:
                raise ValueError("Level of compression must be between 0 and 9.")
            
            # Compress the data
            gzip_data: bytes = gzip.compress(pickle.dumps(cache_bank), level_compression)
            if not isinstance(gzip_data, bytes):
                raise TypeError("Compressed data must result in a bytes object.")
            
            return gzip_data
        except Exception as e:
            LOGGER.error(f"Error making gzip: {e}")
            raise e

    def _make_json(self, cache_bank: OrderedDict[str, OrderedDict[Tuple, Any]]) -> bytes:
        """
        _make_json
        ==========
        Converts the cache bank to a json object.

        Arguments:
            cache_bank (OrderedDict) :
                The cache bank to convert.

        Returns:
            out (bytes) :
                The json data.
        """
        def custom_serializer(obj):
            """
            Custom serializer for non-serializable objects.
            """
            if isinstance(obj, tuple):
                return {"__tuple__": list(obj)}  # Mark tuples for decoding
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        try:
            # Convert tuple keys to strings
            serializable_cache_bank = self._convert_tuple_key_to_string(cache_bank)
            
            # Serialize the cache_bank to JSON
            json_data: str = json.dumps(serializable_cache_bank, default=custom_serializer)
            byte_json_data: bytes = json_data.encode("utf-8")
            
            if not isinstance(byte_json_data, bytes):
                raise TypeError("JSON data must result in a bytes object.")
            
            return byte_json_data
        except Exception as e:
            LOGGER.error(f"Error making json: {e}")
            raise e

    def _make_yaml(self, cache_bank: OrderedDict) -> bytes:
        """
        _make_yaml
        ==========
        Converts the cache bank to a yaml object.

        Arguments:
            cache_bank (OrderedDict) :
                The cache bank to convert.

        Returns:
            out (bytes) :
                The yaml data.
        """
        def ordered_dict_representer(dumper, data):
            """
            Custom representer for OrderedDict.
            Converts OrderedDict to a regular dictionary for YAML serialization.
            """
            return dumper.represent_dict(data.items())
        
        try:
            # Register the custom representer for OrderedDict
            yaml.add_representer(OrderedDict, ordered_dict_representer, Dumper=yaml.SafeDumper)

            # Convert tuple keys to strings
            serializable_cache_bank = self._convert_tuple_key_to_string(cache_bank)

            # Serialize the cache bank to YAML
            yaml_data: str = yaml.dump(serializable_cache_bank, Dumper=yaml.SafeDumper)

            byte_yaml_data: bytes = yaml_data.encode("utf-8")

            if not isinstance(byte_yaml_data, bytes):
                raise TypeError("YAML data must result in a bytes object.")
            if not byte_yaml_data:
                raise ValueError("YAML data must not be empty.")
            
            return byte_yaml_data
        except Exception as e:
            LOGGER.error(f"Error making yaml: {e}")
            raise e

    def _default_map_converters(self) -> Dict[str, Callable]:
        """
        _default_map_converters
        ==============
        Maps the cache type to the corresponding converter function.

        Map:
        -------
        ```python
        map = {
            CacheType.PICKLE: self._make_pickle,
            CacheType.ZLIB: self._make_zlib,
            CacheType.GZIP: self._make_gzip,
            CacheType.JSON: self._make_json,
            CacheType.YAML: self._make_yaml
        }
        ```
        """
        return {
            CacheType.PICKLE: self._make_pickle,
            CacheType.ZLIB: self._make_zlib,
            CacheType.GZIP:self. _make_gzip,
            CacheType.JSON: self._make_json,
            CacheType.YAML: self._make_yaml
        }

