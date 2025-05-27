# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

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
from tests.test_cache_bank import cached_cube

# -------------------------------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------------------------------

@pytest.fixture
def cache_bank():
    """Fixture to create a CacheBank instance for testing."""
    cache_bank: CacheBank = CacheBank()
    # Reset the cache bank to default values
    cache_bank.clear()
    cache_bank.reset_default()
    cache_bank.remove_files()
    return cache_bank

@pytest.fixture
def square_function():
    """A simple function to be used for testing."""
    def square(x: int) -> int:
        if not isinstance(x, int):
            raise TypeError("Input must be an integer")
        if x < 0:
            raise ValueError("Input must be a non-negative integer")
        return x * x
    return square

@pytest.fixture
def cube_function():
    """A simple function to be used for testing."""
    def cube(x: int) -> int:
        if not isinstance(x, int):
            raise TypeError("Input must be an integer")
        if x < 0:
            raise ValueError("Input must be a non-negative integer")
        return x * x * x
    return cube

@pytest.fixture
def sum_function():
    """A simple function to be used for testing."""
    def sum_func(x: int, y: int) -> int:
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("Inputs must be integers")
        return x + y
    return sum_func

# -------------------------------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------------------------------

def test_cache_bank_lru(cache_bank: CacheBank, square_function, cube_function, sum_function) -> None:
    """Test the LRU cache functionality of CacheBank."""

    # Set Maximum bank size
    cache_bank.max_bank_size = 2

    # Set cache type to LRU
    cache_bank.lru = True

    # Wrap the square function with the cache bank
    cached_square: Callable= cache_bank(square_function)
    # Wrap the cube function with the cache bank
    cached_cube: Callable = cache_bank(cube_function)

    # Test caching functionality
    for i in range(10):
        _ = cached_square(i)

    for i in range(10):
        _ = cached_cube(i)

    cache_bank.print_full_report()

    # Check if the cache size is correct
    assert cache_bank.bank_length == 2, "Cache size should be 2 after adding 2 funcs."

    # add one more item to exceed the cache size
    cached_sum: Callable = cache_bank(sum_function)
    _ = cached_sum(1, 2)

    cache_bank.print_full_report()

    # Check if the cache size is still 10 (LRU eviction should occur)
    assert cache_bank.bank_length == 2, "Cache size should still be 2 after adding 3 items."


def test_cache_bank_total_mem_lru(cache_bank: CacheBank, square_function, cube_function, sum_function) -> None:
    """Test the total memory usage of the LRU cache in CacheBank."""

    # Set Maximum bank size
    cache_bank.max_bank_size = 100

    # Set cache type to LRU
    cache_bank.lru = True

    # Set the maximum memory size for each function
    cache_bank.max_func_memory_size = CacheSize.E_128KB

    # Set Max mem size
    cache_bank.max_total_memory_size = CacheSize.E_256KB

    # wrap the square function with the cache bank
    cached_square: Callable = cache_bank(square_function)
    cached_cube: Callable = cache_bank(cube_function)
    cached_sum: Callable = cache_bank(sum_function)

    print("Total memory size of the cache bank before:", sys.getsizeof(cache_bank.cache_bank))

    for i in range(200):
        _ = cached_square(i)

    for i in range(200):
        _ = cached_cube(i)

    for i in range(200):
        _ = cached_sum(i, i + 1)
        
    assert sys.getsizeof(cache_bank.cache_bank) <= cache_bank.max_total_memory_size.value, \
        "Total memory size of the cache bank should not exceed the maximum limit."
    

def test_cache_bank_default_mem_func_lru(cache_bank: CacheBank, square_function) -> None:
    """Test the default memory size of the LRU cache in CacheBank."""

    # Set Maximum bank size
    cache_bank.max_bank_size = 100

    # Set cache type to LRU
    cache_bank.lru = True

    # wrap the square function with the cache bank
    cached_square: Callable = cache_bank(square_function)

    for i in range(200):
        _ = cached_square(i)
    
    assert sys.getsizeof(cache_bank.cache_bank) <= cache_bank.max_func_memory_size, \
        "Total func memory size of the cache bank should not exceed the maximum limit."
    
    assert len(cache_bank.cache_bank["square"]) < 200, \
        "Cache size for square_function should be less than 200 after LRU eviction."


def test_cache_bank_specific_mem_func_lru(cache_bank: CacheBank, square_function) -> None:
    """Test the specific memory size of the LRU cache in CacheBank."""

    # Set Maximum bank size
    cache_bank.max_bank_size = 100

    # Set cache type to LRU
    cache_bank.lru = True

    # Set the maximum memory size for the square function
    cache_bank(square_function, CacheSize.E_1KB)  

    # wrap the square function with the cache bank
    cached_square: Callable = cache_bank(square_function)

    for i in range(5):
        _ = cached_square(i)

    cache_bank.print()

    print(cache_bank.func_size_dict)

    print("Total memory size of the cache bank after:", sys.getsizeof(cache_bank.cache_bank["square"]))
    
    assert len(cache_bank.cache_bank["square"]) < 5, \
        "Cache size for square_function should be less than 5 after LRU eviction."


def test_cache_bank_wrap_specific_mem_func_lru(cache_bank: CacheBank) -> None:
    """Test wrapping a function with specific memory size in the LRU cache of CacheBank."""

    # Set Maximum bank size
    cache_bank.max_bank_size = 100

    # Set cache type to LRU
    cache_bank.lru = True

    @cache_bank.wrapper(CacheSize.E_1KB)
    def square(x: int) -> int:
        """A simple square function."""
        if not isinstance(x, int):
            raise TypeError("Input must be an integer")
        if x < 0:
            raise ValueError("Input must be a non-negative integer")
        return x * x

    for i in range(5):
        _ = square(i)

    cache_bank.print()

    print(cache_bank.func_size_dict)

    assert len(cache_bank.cache_bank["square"]) < 5, \
        "Cache size for square_function should be less than 5 after LRU eviction."
  
