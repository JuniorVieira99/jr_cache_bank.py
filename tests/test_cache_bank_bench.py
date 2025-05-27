# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import pytest
import time
import sys

from typing import Callable

# Local imports
from jr_cache_bank.cache.cache_bank import CacheBank
from jr_cache_bank.cache.cache_enums import CacheSize

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

@pytest.fixture
def factorial() -> Callable:
    """Fixture to create a Factorial function."""
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n * factorial(n - 1)
    return factorial

@pytest.fixture
def sum_of_squares() -> Callable:
    """Fixture to create a Sum of Squares function."""
    def sum_of_squares(n):
        return sum(i * i for i in range(n + 1))
    return sum_of_squares

@pytest.fixture
def time_consuming_function() -> Callable:
    """Fixture to create a time-consuming function."""
    def time_consuming_function(n: int) -> int:
        time.sleep(n)
        return n
    return time_consuming_function

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


def test_cache_bank_factorial_500(cache_bank, factorial) -> None:
    """Test the Factorial function with caching."""
    
    print("Testing Factorial function with caching...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_128KB

    cached_factorial = cache_bank(factorial)
    
    start_time: float = time.time()

    print("Calling the Factorial function 1000 times...")
    # Call the factorial function 500 times
    for i in range(500):
        _ = cached_factorial(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached Factorial: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(500):
        assert cache_bank.get(cached_factorial, (i,)) == cached_factorial(i)

    print("Calling the Factorial function ...")

    start_time: float = time.time()

    # Call the factorial function again
    for i in range(500):
        _ = cached_factorial(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached Factorial: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'factorial': {sys.getsizeof(cache_bank.cache_bank['factorial'])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(cached_factorial)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")


def test_cache_bank_sum_of_squares_500(cache_bank, sum_of_squares) -> None:
    """Test the Sum of Squares function with caching."""
    
    print("Testing Sum of Squares function with caching...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_256KB

    cached_sum_of_squares = cache_bank(sum_of_squares)
    
    start_time: float = time.time()

    print("Calling the Sum of Squares function 500 times...")
    # Call the sum_of_squares function 500 times
    for i in range(500):
        _ = cached_sum_of_squares(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached Sum of Squares: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(500):
        assert cache_bank.get(cached_sum_of_squares, (i,)) == cached_sum_of_squares(i)

    print("Calling the Sum of Squares function ...")

    start_time: float = time.time()

    # Call the sum_of_squares function again
    for i in range(500):
        _ = cached_sum_of_squares(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached Sum of Squares: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'sum_of_squares': {sys.getsizeof(cache_bank.cache_bank['sum_of_squares'])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(cached_sum_of_squares)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")


def test_cache_bank_time_consuming_function(cache_bank, time_consuming_function) -> None:
    """Test the Time Consuming function with caching."""
    
    print("Testing Time Consuming function with caching...")
    print(f"Cache bank object before caching: {sys.getsizeof(cache_bank)} bytes")

    cache_bank.max_func_memory_size = CacheSize.E_128KB

    cached_time_consuming_function = cache_bank(time_consuming_function)
    
    start_time: float = time.time()

    print("Calling the Time Consuming function 5 times...")
    # Call the time_consuming_function 5 times
    for i in range(5):
        _ = cached_time_consuming_function(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for not yet cached Time Consuming function: {elapsed_time:.4f} seconds")

    print("Checking the cache bank...")
    # Check that the result is correct
    for i in range(5):
        assert cache_bank.get(cached_time_consuming_function, (i,)) == i

    print("Calling the Time Consuming function ...")

    start_time: float = time.time()

    # Call the time_consuming_function again
    for i in range(5):
        _ = cached_time_consuming_function(i)

    end_time: float = time.time()

    # Calculate the elapsed time
    elapsed_time: float = end_time - start_time
    print(f"Elapsed time for cached Time Consuming function: {elapsed_time:.4f} seconds")
    
    print(f"Cache bank object size after caching: {sys.getsizeof(cache_bank)} bytes")
    print(f"Size of the cached entry 'time_consuming_function': {sys.getsizeof(cache_bank.cache_bank['time_consuming_function'])} bytes")

    cache_bank.print_cache_report()
    cache_bank.print_func_stats(cached_time_consuming_function)

    # Clean up the cache bank
    cache_bank.clear()
    cache_bank.reset_default()

    # Remove all cache files
    cache_bank.remove_files()

    print("Test completed successfully.")

