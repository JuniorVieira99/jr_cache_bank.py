# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import pytest
import time
import os
import sys

from typing import Callable, Final
from collections import OrderedDict

# Local imports
from jr_cache_bank.cache.cache_bank import CacheBank
from jr_cache_bank.cache.cache_enums import CacheType, CacheSize

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
def fibonacci() -> Callable:
    """Fixture to create a Fibonacci function."""
    def fibonacci(n):
        if n <= 1:
            return n
        else:
            return fibonacci(n - 1) + fibonacci(n - 2)
    return fibonacci


# -------------------------------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------------------------------

def test_cache_bank_cached_square_500(cache_bank) -> None:
    """Test the initialization of the CacheBank."""
    
    print("Testing cached square function with 500 calls...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_128KB

    @cache_bank.wrapper()
    def square(x):
        return x * x
    
    start_time: float = time.time()

    print("Calling the cached square function 500 times...")
    # Call the cached_square function 1000 times
    for i in range(500):
        _ = square(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached square: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(500):
        assert cache_bank.get(square, (i,)) == i * i

    print("Calling the cached square ...")

    start_time: float = time.time()

    # Call the cached_square function again
    for i in range(500):
        _ = square(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached square: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'square': {sys.getsizeof(cache_bank.cache_bank["square"])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(square)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")


def test_cache_bank_cached_square_1000(cache_bank) -> None:
    """Test the initialization of the CacheBank."""
    
    print("Testing cached square function with 1000 calls...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_128KB

    @cache_bank.wrapper()
    def square(x):
        return x * x
    
    start_time: float = time.time()

    print("Calling the cached square function 1000 times...")
    # Call the cached_square function 1000 times
    for i in range(1000):
        _ = square(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached square: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(1000):
        assert cache_bank.get(square, (i,)) == i * i

    print("Calling the cached square ...")

    start_time: float = time.time()

    # Call the cached_square function again
    for i in range(1000):
        _ = square(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached square: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'square': {sys.getsizeof(cache_bank.cache_bank["square"])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(square)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")


def test_cache_bank_fibonacci_30(cache_bank, fibonacci) -> None:
    """Test the Fibonacci function with caching."""
    
    print("Testing Fibonacci function with caching...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_128KB

    cached_fibonacci = cache_bank(fibonacci)
    
    start_time: float = time.time()

    print("Calling the Fibonacci function 30 times...")
    # Call the fibonacci function 30 times
    for i in range(30):
        _ = cached_fibonacci(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached Fibonacci: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(30):
        assert cache_bank.get(cached_fibonacci, (i,)) == cached_fibonacci(i)

    print("Calling the Fibonacci function ...")

    start_time: float = time.time()

    # Call the fibonacci function again
    for i in range(30):
        _ = cached_fibonacci(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached Fibonacci: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'fibonacci': {sys.getsizeof(cache_bank.cache_bank['fibonacci'])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(cached_fibonacci)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")


def test_cache_bank_fibonacci_35(cache_bank, fibonacci) -> None:
    """Test the Fibonacci function with caching."""
    
    print("Testing Fibonacci function with caching...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_128KB

    cached_fibonacci = cache_bank(fibonacci)
    
    start_time: float = time.time()

    print("Calling the Fibonacci function 35 times...")
    # Call the fibonacci function 35 times
    for i in range(35):
        _ = cached_fibonacci(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached Fibonacci: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(35):
        assert cache_bank.get(cached_fibonacci, (i,)) == cached_fibonacci(i)

    print("Calling the Fibonacci function ...")

    start_time: float = time.time()

    # Call the fibonacci function again
    for i in range(35):
        _ = cached_fibonacci(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached Fibonacci: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'fibonacci': {sys.getsizeof(cache_bank.cache_bank['fibonacci'])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(cached_fibonacci)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")

