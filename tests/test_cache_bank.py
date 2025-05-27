# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

from pathlib import Path
import pytest
import sys
import os
import json

from typing import Callable, Final
from collections import OrderedDict
# Local imports
from jr_cache_bank.cache.cache_bank import CacheBank, CacheType
from jr_cache_bank.cache.cache_enums import CacheSize
from jr_cache_bank.exceptions.exceptions_cache_bank import (
    CacheBankConstructionError,
    CacheBankSetError,
    CacheBankMakeHashableError,
    CacheBankSaveError,
    CacheBankLoadError,
)

# -------------------------------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------------------------------

@pytest.fixture
def cache_bank():
    """Fixture to create a CacheBank instance for testing."""
    cache_bank: CacheBank = CacheBank()
    # Reset the cache bank to default values
    cache_bank.reset_default()
    return cache_bank

@pytest.fixture
def uncached_square() -> Callable:
    """Fixture to create a function that squares a number without caching."""
    def square(x):
        return x * x
    return square

@pytest.fixture
def cached_square(cache_bank) -> Callable:
    """Fixture to create a function that squares a number with caching."""
    @cache_bank.wrapper()
    def square(x):
        return x * x
    return square

@pytest.fixture
def uncached_cube() -> Callable:
    """Fixture to create a function that cubes a number without caching."""
    def cube(x):
        return x * x * x
    return cube

@pytest.fixture
def cached_cube(cache_bank) -> Callable:
    """Fixture to create a function that cubes a number with caching."""
    @cache_bank.wrapper()
    def cube(x):
        return x * x * x
    return cube

@pytest.fixture
def config_dict() -> dict:
    """Fixture to create a configuration dictionary for testing."""
    return {
        "max_bank_size": 100,
        "lru": True,
        "max_file_size": 100000,
        "cache_type": CacheType.PICKLE,
        "cache_bank": OrderedDict({}),
        "filename": "my_cache.pkl",
        "max_total_memory_size": CacheSize.E_10MB,
        "max_func_memory_size": CacheSize.E_10KB,
    }


# -------------------------------------------------------------------------------------------------
# Test Cases
# -------------------------------------------------------------------------------------------------

INT_MAX_BANK_SIZE_ERRORS: Final = [
    # max_bank_size (int), lru (bool), max_file_size (int), cache_type (CacheType), cache_bank (dict), filename (str |Path)
    ("",True, 1000, CacheType.PICKLE),
    (0,True, 1000, CacheType.PICKLE),
    (-1,True, 1000, CacheType.PICKLE),
    ([],True, 1000, CacheType.PICKLE),
    ({},True, 1000, CacheType.PICKLE),
    ((),True, 1000, CacheType.PICKLE),
]

INIT_LRU_ERRORS: Final = [
    # max_bank_size (int), lru (bool), max_file_size (int), cache_type (CacheType), cache_bank (dict), filename (str |Path)
    (100,100, 1000, CacheType.PICKLE),
    (100,"100", 1000, CacheType.PICKLE),
    (100,[], 1000, CacheType.PICKLE),
    (100,{}, 1000, CacheType.PICKLE),
    (100,(), 1000, CacheType.PICKLE),
]

INIT_MAX_FILE_SIZE_ERRORS: Final = [
    # max_bank_size (int), lru (bool), max_file_size (int), cache_type (CacheType), cache_bank (dict), filename (str |Path)
    (100,True, "", CacheType.PICKLE),
    (100,True, 0, CacheType.PICKLE),
    (100,True, -1, CacheType.PICKLE),
    (100,True, [], CacheType.PICKLE),
    (100,True, {}, CacheType.PICKLE),
    (100,True, (), CacheType.PICKLE)
]

INIT_CACHE_TYPE_ERRORS: Final = [
    # max_bank_size (int), lru (bool), max_file_size (int), cache_type (CacheType), cache_bank (dict), filename (str |Path)
    (100,True, 1000, 100),
    (100,True, 1000, ""),
    (100,True, 1000, []),
    (100,True, 1000, {}),
    (100,True, 1000, ())
]

INIT_CACHE_BANK_ERRORS: Final = [
    # max_bank_size (int), lru (bool), max_file_size (int), cache_type (CacheType), cache_bank (dict), filename (str |Path)
    (100,True, 1000, CacheType.PICKLE, 100),
    (100,True, 1000, CacheType.PICKLE, ""),
    (100,True, 1000, CacheType.PICKLE, []),
    (100,True, 1000, CacheType.PICKLE, 5.5),
    (100,True, 1000, CacheType.PICKLE, ())
]

INIT_FILENAME_ERRORS: Final = [
    # max_bank_size (int), lru (bool), max_file_size (int), cache_type (CacheType), cache_bank (dict), filename (str |Path)
    (100,True, 1000, CacheType.PICKLE, OrderedDict({}), 100),
    (100,True, 1000, CacheType.PICKLE, OrderedDict({}), ""),
    (100,True, 1000, CacheType.PICKLE, OrderedDict({}), []),
    (100,True, 1000, CacheType.PICKLE, OrderedDict({}), {}),
    (100,True, 1000, CacheType.PICKLE, OrderedDict({}), ()),
    (100,True, 1000, CacheType.PICKLE, OrderedDict({}), 5.5)
]

INIT_MAX_TOTAL_MEMORY_ERRORS: Final = [
    # max_total_memory
    -1, {}, [], (), 0, "100"
]

INIT_MAX_FUNC_MEMORY_SIZE_ERRORS: Final = [
    # max_func_memory_size
    -1, {}, [], (), 0, "100"
]

SETTER_MAX_BANK_SIZE_ERRORS: Final = [-1, {}, [], (), "-1"]

SETTER_LRU_ERRORS: Final = [100, {}, [], (), "100"]

SETTER_MAX_FILE_SIZE_ERRORS: Final = [-1, {}, [], (), "100"]

SETTER_CACHE_TYPE_ERRORS: Final = [100, {}, [], (), 0]

SETTER_CACHE_BANK_ERRORS: Final = [100, True, [], (), 0]

SETTER_FILENAME_ERRORS: Final = [100, True, {}, [], 0, ""]

SAVE_CACHE_TYPES_VARS: Final = [
    (CacheType.PICKLE, ".pkl"), 
    (CacheType.GZIP,  ".gz"),
    (CacheType.ZLIB, ".zlib"),
    (CacheType.JSON, ".json"),
    (CacheType.YAML, ".yaml")
]

MAKE_HASHABLE_ERRORS: Final = [
    # function (Callable), args (tuple), kwargs (dict)
    (None, None, None),
    ("", None, None),
    ([], None, None),
    ({}, None, None),
    ((), None, None),
    (1, None, None),
    (1.0, None, None),
    (True, None, None),
    (False, None, None)
]

# -------------------------------------------------------------------------------------------------
# Edge Tests
# -------------------------------------------------------------------------------------------------

# Initialization Tests

def test_cache_bank_init(cache_bank):
    """Test the initialization of the CacheBank class."""
    assert isinstance(cache_bank, CacheBank)
    assert cache_bank.max_bank_size == 100
    assert cache_bank.lru is True
    assert cache_bank.max_file_size == 100000
    assert cache_bank.cache_type == CacheType.PICKLE

@pytest.mark.parametrize(
    "max_bank_size, lru, max_file_size, cache_type",
    INIT_MAX_FILE_SIZE_ERRORS
)
def test_init_max_file_size_errors(max_bank_size, lru, max_file_size, cache_type):
    """Test the initialization of the CacheBank class with invalid max_file_size."""
    with pytest.raises(CacheBankConstructionError):
        CacheBank(max_bank_size=max_bank_size, lru=lru, max_file_size=max_file_size, cache_type=cache_type)

@pytest.mark.parametrize(
    "max_bank_size, lru, max_file_size, cache_type",
    INIT_LRU_ERRORS
)
def test_init_lru_errors(max_bank_size, lru, max_file_size, cache_type):
    """Test the initialization of the CacheBank class with invalid lru."""
    with pytest.raises(CacheBankConstructionError):
        CacheBank(max_bank_size=max_bank_size, lru=lru, max_file_size=max_file_size, cache_type=cache_type)

@pytest.mark.parametrize(
    "max_bank_size, lru, max_file_size, cache_type",
    INIT_CACHE_TYPE_ERRORS
)
def test_init_cache_type_errors(max_bank_size, lru, max_file_size, cache_type):
    """Test the initialization of the CacheBank class with invalid cache_type."""
    with pytest.raises(CacheBankConstructionError):
        CacheBank(max_bank_size=max_bank_size, lru=lru, max_file_size=max_file_size, cache_type=cache_type)

@pytest.mark.parametrize(
    "max_bank_size, lru, max_file_size, cache_type, var_cache_bank",
    INIT_CACHE_BANK_ERRORS
)
def test_init_cache_bank_errors(max_bank_size, lru, max_file_size, cache_type, var_cache_bank):
    """Test the initialization of the CacheBank class with invalid cache_bank."""
    with pytest.raises(CacheBankConstructionError):
        CacheBank(max_bank_size=max_bank_size, lru=lru, max_file_size=max_file_size, cache_type=cache_type, cache_bank=var_cache_bank)

@pytest.mark.parametrize(
    "max_total_memory_size",
    INIT_MAX_TOTAL_MEMORY_ERRORS
)
def test_init_max_total_memory_errors(max_total_memory_size):
    """Test the initialization of the CacheBank class with invalid max_total_memory_size."""
    with pytest.raises(CacheBankConstructionError):
        CacheBank(max_total_memory_size=max_total_memory_size)

@pytest.mark.parametrize(
    "max_func_memory_size",
    INIT_MAX_FUNC_MEMORY_SIZE_ERRORS
)
def test_init_max_func_memory_size_errors(max_func_memory_size):
    """Test the initialization of the CacheBank class with invalid max_func_memory_size."""
    with pytest.raises(CacheBankConstructionError):
        CacheBank(max_func_memory_size=max_func_memory_size)

# Filename Tests

@pytest.mark.parametrize(
    "filename",
    INIT_FILENAME_ERRORS
)
def test_save_filename_errors(cache_bank, filename):
    """Test the save method of the CacheBank class with invalid filename."""
    with pytest.raises(CacheBankSaveError):
        cache_bank.save(filename)

@pytest.mark.parametrize(
    "filename",
    INIT_FILENAME_ERRORS
)
def test_load_filename_errors(cache_bank, filename):
    """Test the load method of the CacheBank class with invalid filename."""
    with pytest.raises(CacheBankLoadError):
        cache_bank.load(filename)

# Make Hashable Tests

@pytest.mark.parametrize(
    "function, args, kwargs",
    MAKE_HASHABLE_ERRORS
)
def test_make_hashable_errors(cache_bank, function, args, kwargs):
    """Test the make_hashable method of the CacheBank class with invalid inputs."""
    with pytest.raises(CacheBankMakeHashableError):
        cache_bank.make_hashable(function, args, kwargs)

# Setters Tests

@pytest.mark.parametrize(
    "max_bank_size",
    SETTER_MAX_BANK_SIZE_ERRORS
)
def test_setter_max_bank_size_errors(cache_bank, max_bank_size):
    """Test the setter for max_bank_size with invalid values."""
    with pytest.raises(CacheBankSetError):
        cache_bank.max_bank_size = max_bank_size

@pytest.mark.parametrize(
    "lru",
    SETTER_LRU_ERRORS
)
def test_setter_lru_errors(cache_bank, lru):
    """Test the setter for lru with invalid values."""
    with pytest.raises(CacheBankSetError):
        cache_bank.lru = lru

@pytest.mark.parametrize(
    "max_file_size",
    SETTER_MAX_FILE_SIZE_ERRORS
)
def test_setter_max_file_size_errors(cache_bank, max_file_size):
    """Test the setter for max_file_size with invalid values."""
    with pytest.raises(CacheBankSetError):
        cache_bank.max_file_size = max_file_size

@pytest.mark.parametrize(
    "cache_type",
    SETTER_CACHE_TYPE_ERRORS
)
def test_setter_cache_type_errors(cache_bank, cache_type):
    """Test the setter for cache_type with invalid values."""
    with pytest.raises(CacheBankSetError):
        cache_bank.cache_type = cache_type

@pytest.mark.parametrize(
    "var_cache_bank",
    SETTER_CACHE_BANK_ERRORS
)
def test_setter_cache_bank_errors(cache_bank, var_cache_bank):
    """Test the setter for cache_bank with invalid values."""
    with pytest.raises(CacheBankSetError):
        cache_bank.cache_bank = cache_bank

@pytest.mark.parametrize(
    "filename",
    SETTER_FILENAME_ERRORS
)
def test_setter_filename_errors(cache_bank, filename):
    """Test the setter for filename with invalid values."""
    with pytest.raises(CacheBankSetError):
        cache_bank.filename = filename

@pytest.mark.parametrize(
    "filename",
    INIT_FILENAME_ERRORS
)
def test_file_validator(cache_bank, filename):
    """Test the file validator method of the CacheBank class with invalid filename."""
    with pytest.raises(Exception):
        cache_bank.file_validator(filename)


# -------------------------------------------------------------------------------------------------
# Cache Tests
# -------------------------------------------------------------------------------------------------

def test_cache_function(cache_bank, uncached_square):
    """Test the cache decorator."""

    for i in range(5):
        result:int = uncached_square(i)
        cache_bank.set(uncached_square, args=(i,), kwargs={}, result=result)

    for i in range(5):
        result: int = uncached_square(i)
        cached_result:int = cache_bank.get(uncached_square, args=(i,), kwargs={})
        assert result == cached_result
    
    # Clear the cache bank
    cache_bank.clear()
    # Reset the cache bank to default values
    cache_bank.reset_default()
    
def test_cache_function_with_kwargs(cache_bank, uncached_square):
    """Test the cache decorator with keyword arguments."""
    for i in range(5):
        result:int = uncached_square(i)
        cache_bank.set(uncached_square, kwargs={"x": i}, result=result)

    for i in range(5):
        result: int = uncached_square(i)
        cached_result:int = cache_bank.get(uncached_square, kwargs={"x": i})
        assert result == cached_result

    # Clear the cache bank
    cache_bank.clear()
    # Reset the cache bank to default values
    cache_bank.reset_default()

def test_cache_wrapper(cache_bank, cached_square):
    """Test the cache wrapper."""
    for i in range(5):
        cached_square(i)

    for i in range(10):
        cached_square(i)

    print(f"Cache Report: {cache_bank.print_cache_report()}")

    assert cache_bank.cached_reporter.hits == 5
    assert cache_bank.cached_reporter.misses == 9

    # Clear the cache bank
    cache_bank.clear()
    # Reset the cache bank to default values
    cache_bank.reset_default()

def test_cache_callable(cache_bank, uncached_square):
    """Test the cache callable."""
    wrapped_func: Callable = cache_bank(uncached_square)
    for i in range(5):
        wrapped_func(i)

    for i in range(10):
        wrapped_func(i)

    assert cache_bank.get(uncached_square, args=(1,), kwargs={}) == 1
    assert cache_bank.get(uncached_square, args=(2,), kwargs={}) == 4
    
    print(f"Cache Report: {cache_bank.print_cache_report()}")

    # Clear the cache bank
    cache_bank.clear()
    # Reset the cache bank to default values
    cache_bank.reset_default()

def test_save_cache_bank(cache_bank, tmp_path, uncached_square):
    """Test the save method of the CacheBank class."""

    temp_file: Path = tmp_path / "test_file.pkl"

    cache_bank.set(uncached_square,args=(1,), kwargs={}, result=1)
    cache_bank.set(uncached_square,args=(2,), kwargs={}, result=4)

    cache_bank.save(temp_file)

    try:
        with open(temp_file, "rb") as f:
            data = f.read()
            assert data is not None
    except FileNotFoundError as e:
        print("File not found, skipping test.")
        raise e
    
def test_load_cache_bank(cache_bank, tmp_path, uncached_square):

    temp_file: Path = tmp_path / "test_file.pkl"
    
    cache_bank.set(uncached_square, args=(1,), kwargs={}, result=1)
    cache_bank.set(uncached_square, args=(2,), kwargs={}, result=4)

    cache_bank.save(temp_file)

    with open(temp_file, "rb") as f:
        data = f.read()
        assert data is not None
    
    cache_bank.clear()

    # Load the cache bank from the file
    cache_bank.load(temp_file)

    # Check if the cache bank contains the correct data
    assert cache_bank.get(uncached_square, args=(1,), kwargs={}) == 1
    assert cache_bank.get(uncached_square, args=(2,), kwargs={}) == 4

@pytest.mark.parametrize(
    "cache_type, suffix",
    SAVE_CACHE_TYPES_VARS
)
def test_save_cache_bank_with_different_types(cache_bank, tmp_path, uncached_square, cache_type, suffix):
    """Test the save method of the CacheBank class with different cache types."""
    cache_bank.cache_type = cache_type
    temp_file = tmp_path / f"test_file{suffix}"
    
    cache_bank.set(uncached_square, args=(1,), kwargs={}, result=1)
    cache_bank.set(uncached_square, args=(2,), kwargs={}, result=4)

    cache_bank.save(temp_file)

    with open(temp_file, "rb") as f:
        data = f.read()
        assert data is not None
    
    # Clear the cache bank
    cache_bank.clear()

    # assert that the cache bank is empty
    assert cache_bank.is_empty() is True

    # Load the cache bank from the file
    cache_bank.load(temp_file)

    # Check if the cache bank contains the correct data
    assert cache_bank.get(uncached_square, args=(1,), kwargs={}) == 1
    assert cache_bank.get(uncached_square, args=(2,), kwargs={}) == 4

    # Reset the cache bank to default values
    cache_bank.reset_default()


# -------------------------------------------------------------------------------------------------
# Functionality Tests
# ------------------------------------------------------------------------------------------------- 

def test_keys(cache_bank, cached_square):
    """Test the keys method of the CacheBank class."""
    for i in range(5):
        cached_square(i)

    keys = cache_bank.keys()
    assert len(keys) == 1

    print("Keys in the cache bank:")
    for i in keys:
        print(f"Key: {i}")
    
    # Clear the cache bank
    cache_bank.clear()

def test_values(cache_bank, cached_square):
    """Test the values method of the CacheBank class."""
    for i in range(5):
        cached_square(i)

    values = cache_bank.values()
    assert len(values) == 1

    print("Values in the cache bank:")
    for i, dc in enumerate(values):
        print(f"Value: {dc}")
        assert dc[('square', (i,))] == i * i 

    # Clear the cache bank
    cache_bank.clear()

    # Reset the cache bank to default values
    cache_bank.reset_default()

def test_clear(cache_bank, cached_square):
    """Test the clear method of the CacheBank class."""
    for i in range(5):
        cached_square(i)

    assert len(cache_bank.cache_bank) == 1

    cache_bank.clear()

    assert len(cache_bank.cache_bank) == 0
    assert cache_bank.cached_reporter.hits == 0
    assert cache_bank.cached_reporter.misses == 0
    assert cache_bank.cached_reporter.total == 0

    print("Cache bank cleared.")

def test_is_empty(cache_bank, cached_square):
    """Test the is_empty method of the CacheBank class."""
    assert cache_bank.is_empty() is True

    for i in range(5):
        cached_square(i)

    assert cache_bank.is_empty() is False

    cache_bank.clear()

    assert cache_bank.is_empty() is True

    print("Cache bank is empty.")

def test_is_full(cache_bank, cached_square):
    """Test the is_full method of the CacheBank class."""
    assert cache_bank.is_full() is False

    # Set the maximum size of the cache bank to 5
    cache_bank.max_bank_size = 1

    cached_square(1)

    assert cache_bank.is_full() is True

    cache_bank.clear()

    assert cache_bank.is_full() is False

    # Reset the cache bank
    cache_bank.reset_default()

    print("Cache bank is full.")

def test_lru(cache_bank, cached_square, cached_cube):
    """Test the LRU (Least Recently Used) functionality of the CacheBank class."""
    # Set the maximum size of the cache bank to 5
    cache_bank.max_bank_size = 1
    cache_bank.lru = True

    for i in range(5):
        cached_square(i)

    # Check if the cache bank is full
    assert cache_bank.is_full() is True

    # Make the last accessed item the most recently used
    cached_square(0)

    # Add more elements to exceed the max bank size
    for i in range(5):
        cached_cube(i)

    print("Cache bank after adding more elements:")
    cache_bank.print_full_report()

    # Check if length of cache bank is equal to max bank size
    assert len(cache_bank.cache_bank) == 1
    # Check if the least recently used item (0) is removed
    assert cache_bank.get(cached_square, args=(0,), kwargs={}) is None

    # Reset the cache bank
    cache_bank.reset_default()

def test_total_mem_lru(cache_bank, cached_square):
    """Test the total memory LRU (Least Recently Used) functionality of the CacheBank class."""
    # Set the maximum size of the cache bank to 5
    with pytest.raises(CacheBankSetError):
        cache_bank.max_total_memory_size = 1

def test_func_mem_lru(cache_bank, cached_square):
    """Test the function memory LRU (Least Recently Used) functionality of the CacheBank class."""
    with pytest.raises(CacheBankSetError):
        cache_bank.max_func_memory_size = 1
        
# -------------------------------------------------------------------------------------------------
# Config Tests
# -------------------------------------------------------------------------------------------------

def test_static_config_dict(config_dict):
    """Test the static config dictionary of the CacheBank class."""

    cache: CacheBank = CacheBank.static_config_from_dict(config_dict) 

    assert isinstance(cache, CacheBank) , "CacheBank object not created from static config dict"
    assert cache.max_bank_size == 100 , f"max_bank_size not set correctly, got {cache.max_bank_size}, expected 100"
    assert cache.lru is True , f"lru not set correctly, got {cache.lru}, expected True"
    assert cache.max_file_size == 100000 , f"max_file_size not set correctly, got {cache.max_file_size}, expected 100000"
    assert cache.cache_type == CacheType.PICKLE , f"cache_type not set correctly, got {cache.cache_type}, expected CacheType.PICKLE"
    assert cache.cache_bank == OrderedDict({}) , f"cache_bank not set correctly, got {cache.cache_bank}, expected OrderedDict"
    assert cache.max_total_memory_size == CacheSize.E_10MB, f"max_total_memory_size not set correctly, got {cache.max_total_memory_size}, expected CacheSize.E_10MB"
    assert cache.max_func_memory_size == CacheSize.E_10KB , f"max_func_memory_size not set correctly, got {cache.max_func_memory_size}, expected CacheSize.E_10KB"

def test_static_config_json(config_dict):
    """Test the static config JSON method of the CacheBank class."""

    json_data: bytes = json.dumps(config_dict, ).encode("utf-8")

    cache: CacheBank = CacheBank.static_config_from_json(json_data) 

    assert isinstance(cache, CacheBank) , "CacheBank object not created from static config dict"
    assert cache.max_bank_size == 100 , f"max_bank_size not set correctly, got {cache.max_bank_size}, expected 100"
    assert cache.lru is True , f"lru not set correctly, got {cache.lru}, expected True"
    assert cache.max_file_size == 100000 , f"max_file_size not set correctly, got {cache.max_file_size}, expected 100000"
    assert cache.cache_type == CacheType.PICKLE , f"cache_type not set correctly, got {cache.cache_type}, expected CacheType.PICKLE"
    assert cache.cache_bank == OrderedDict({}) , f"cache_bank not set correctly, got {cache.cache_bank}, expected OrderedDict"
    assert cache.max_total_memory_size == CacheSize.E_10MB, f"max_total_memory_size not set correctly, got {cache.max_total_memory_size}, expected CacheSize.E_10MB"
    assert cache.max_func_memory_size == CacheSize.E_10KB , f"max_func_memory_size not set correctly, got {cache.max_func_memory_size}, expected CacheSize.E_10KB"

def test_config_dict(config_dict):
    """Test the config dictionary method of the CacheBank class."""
    cache_bank: CacheBank = CacheBank()
    cache_bank.config_from_dict(config_dict)

    assert isinstance(config_dict, dict) , "config_dict is not a dictionary"
    assert config_dict["max_bank_size"] == 100 , f"max_bank_size not set correctly, got {config_dict['max_bank_size']}, expected 100"
    assert config_dict["lru"] is True , f"lru not set correctly, got {config_dict['lru']}, expected True"
    assert config_dict["max_file_size"] == 100000 , f"max_file_size not set correctly, got {config_dict['max_file_size']}, expected 100000"
    assert config_dict["cache_type"] == CacheType.PICKLE , f"cache_type not set correctly, got {config_dict['cache_type']}, expected CacheType.PICKLE"
    assert config_dict["cache_bank"] == OrderedDict({}) , f"cache_bank not set correctly, got {config_dict['cache_bank']}, expected OrderedDict"
    assert config_dict["max_total_memory_size"] == CacheSize.E_10MB, f"max_total_memory_size not set correctly, got {config_dict['max_total_memory_size']}, expected CacheSize.E_10MB"
    assert config_dict["max_func_memory_size"] == CacheSize.E_10KB , f"max_func_memory_size not set correctly, got {config_dict['max_func_memory_size']}, expected CacheSize.E_10KB"

def test_config_json(config_dict):
    """Test the config JSON method of the CacheBank class."""
    cache_bank: CacheBank = CacheBank()
    json_data: bytes = json.dumps(config_dict).encode("utf-8")
    cache_bank.config_from_json(json_data)

    assert isinstance(json_data, bytes) , "json_data is not a bytes object"
    assert config_dict["max_bank_size"] == 100 , f"max_bank_size not set correctly, got {config_dict['max_bank_size']}, expected 100"
    assert config_dict["lru"] is True , f"lru not set correctly, got {config_dict['lru']}, expected True"
    assert config_dict["max_file_size"] == 100000 , f"max_file_size not set correctly, got {config_dict['max_file_size']}, expected 100000"
    assert config_dict["cache_type"] == CacheType.PICKLE , f"cache_type not set correctly, got {config_dict['cache_type']}, expected CacheType.PICKLE"
    assert config_dict["cache_bank"] == OrderedDict({}) , f"cache_bank not set correctly, got {config_dict['cache_bank']}, expected OrderedDict"
    assert config_dict["max_total_memory_size"] == CacheSize.E_10MB, f"max_total_memory_size not set correctly, got {config_dict['max_total_memory_size']}, expected CacheSize.E_10MB"
    assert config_dict["max_func_memory_size"] == CacheSize.E_10KB , f"max_func_memory_size not set correctly, got {config_dict['max_func_memory_size']}, expected CacheSize.E_10KB"

# -------------------------------------------------------------------------------------------------
# End of File
# -------------------------------------------------------------------------------------------------
