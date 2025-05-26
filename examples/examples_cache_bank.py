# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import time
import sys
from jr_cache_bank.cache.cache_bank import CacheBank, CacheType, CacheSize


# -------------------------------------------------------------------------------------------------
# Example
# -------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    def uncached_square(x: int) ->int:
        if x < 0:
            raise ValueError("x must be positive")
        return x*x

    def example_init():
        print("\n===================================" \
        "\nTest Cache Bank Initialization" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)
        # check if the cache bank is empty
        assert cache.is_empty() == True
        # check if the cache bank is full
        assert cache.is_full() == False
        print(f"Cache Bank Object Size: {sys.getsizeof(cache)} bytes")

    def example_set_get():
        print("\n===================================" \
        "\nTest Cache example_set_get" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)
        # Set the cache bank
        cache.set(uncached_square, args=(2,), kwargs=None, result=4)
        # Get the cache bank
        _ : int = cache.get(uncached_square, args=(2,), kwargs=None)
        
        print("\nChecking Reports:\n")
        cache.print_cache_report()
        cache.print_func_stats(uncached_square)

        # Check bank
        cache.clear()

    def example_set_cache_types():
        print(
            "\n===================================" \
            "\nTest example_set_cache_types" \
            "\n==================================="
        )
        cache : CacheBank = CacheBank(max_bank_size=10, lru=True, cache_type=CacheType.PICKLE)
        # Get filename:
        print(f"Cache PICKLE file name: {cache.filename}")
        # Set CacheType
        cache.cache_type = CacheType.ZLIB
        # Get filename:
        print(f"Cache ZLIB file name: {cache.filename}")
        # Set CacheType
        cache.cache_type = CacheType.GZIP
        # Get filename:
        print(f"Cache GZIP file name: {cache.filename}")
        # Set CacheType
        cache.cache_type = CacheType.PICKLE
        # Get filename:
        print(f"Cache PICKLE file name: {cache.filename}")

    def example_cached_set_get():
        print("\n===================================" \
        "\nTest example_cached_set_get" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)
        
        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        _ : int = cached_square(2)
        print("\nChecking Reports Before:\n")
        # Check report
        cache.print_cache_report()
        cache.print_func_stats(cached_square)

        # Do cached again
        _ : int = cached_square(2)
        # Check report
        print("\nChecking Reports After:\n")
        cache.print_cache_report()
        cache.print_func_stats(cached_square)

        print(len(cache.cache_bank))

        # Check bank
        cache.clear()

    def example_many_funcs():
        print("\n===================================" \
        "\nTest example_many_funcs" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)
        
        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        @cache.wrapper()
        def cached_cube(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x*x

        for i in range(5):
            _ : int = cached_square(i)
            _ : int = cached_cube(i)

        # Check report
        print("\nChecking Reports:\n")
        cache.print_cache_report()
        cache.print_func_stats(cached_square)
        cache.print_func_stats(cached_cube)

        for i in range(10):
            _ : int = cached_square(i)
            _ : int = cached_cube(i)

        print("\nChecking Reports After:\n")
        cache.print_cache_report()
        cache.print_func_stats(cached_square)
        cache.print_func_stats(cached_cube)

    def example_long_func():
        print("\n===================================" \
        "\nTest example_long_func" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)
        
        @cache.wrapper()
        def cached_square(x: int) -> int:
            # Simulate a long function
            time.sleep(1)
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        start = time.time()
        result : int = cached_square(2)
        end = time.time()
        print(f"Time taken for cached_square round 1 : {end - start} seconds")

        assert result == 4

        # Check report
        print("\nChecking Reports:\n")
        cache.print_cache_report()

        # Do cached again
        start = time.time()
        result : int = cached_square(2)
        end = time.time()
        print(f"Time taken for cached_square round 2: {end - start} seconds")

        assert result == 4

        # Check report
        print("\nChecking Reports:\n")
        cache.print_cache_report()

        cache.clear()
        # Check bank

    def example_save_load_pickle():
        print("\n===================================" \
        "\nTest example_save_load_pickle" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=100, lru=True)

        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        for i in range(5):
            _ : int = cached_square(i)
        
        for i in range(10):
            _ : int = cached_square(i)

        # Save the cache bank
        cache.save()

        # Clear the cache bank
        cache.clear()

        # Load the cache bank
        cache.load()

        # Check the cache bank
        cache.print()

        for i in range(10):
            assert cache.get(cached_square, args=(i,), kwargs=None) == i*i , f"Error: {i} not in cache"

        # Remove files
        cache.remove_files()

    def example_save_load_zlib():
        print("\n===================================" \
        "\nTest example_save_load_zlib" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=100, lru=True, cache_type=CacheType.ZLIB)

        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        for i in range(5):
            _ : int = cached_square(i)
        
        for i in range(10):
            _ : int = cached_square(i)

        # Save the cache bank
        cache.save()

        # Clear the cache bank
        cache.clear()

        # Load the cache bank
        cache.load()

        # Check the cache bank
        cache.print()

        for i in range(10):
            assert cache.get(cached_square, args=(i,), kwargs=None) == i*i , f"Error: {i} not in cache"

        # Remove files
        cache.remove_files()

    def example_save_load_gzip():
        print("\n===================================" \
        "\nTest example_save_load_gzip" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=100, lru=True, cache_type=CacheType.GZIP)

        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        for i in range(5):
            _ : int = cached_square(i)
        
        for i in range(10):
            _ : int = cached_square(i)

        # Save the cache bank
        cache.save()

        # Clear the cache bank
        cache.clear()

        # Load the cache bank
        cache.load()

        # Check the cache bank
        cache.print()

        for i in range(10):
            assert cache.get(cached_square, args=(i,), kwargs=None) == i*i , f"Error: {i} not in cache"

        # Remove files
        cache.remove_files()

    def example_save_load_json():
        print("\n===================================" \
        "\nTest example_save_load_json" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=100, lru=True, cache_type=CacheType.JSON)

        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        for i in range(5):
            _ : int = cached_square(i)
        
        for i in range(10):
            _ : int = cached_square(i)

        # Save the cache bank
        cache.save()

        # Clear the cache bank
        cache.clear()

        # Load the cache bank
        cache.load()

        # Check the cache bank
        cache.print()

        for i in range(10):
            assert cache.get(cached_square, args=(i,), kwargs=None) == i*i , f"Error: {i} not in cache"

        # Remove files
        cache.remove_files()

    def example_save_load_yaml():
        print("\n===================================" \
        "\nTest example_save_load_yaml" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=100, lru=True, cache_type=CacheType.YAML)

        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        for i in range(5):
            _ : int = cached_square(i)
        
        for i in range(10):
            _ : int = cached_square(i)

        # Save the cache bank
        cache.save()

        # Clear the cache bank
        cache.clear()

        # Load the cache bank
        cache.load()

        # Check the cache bank
        cache.print()

        for i in range(10):
            assert cache.get(cached_square, args=(i,), kwargs=None) == i*i , f"Error: {i} not in cache"

        # Remove files
        cache.remove_files()

    def example_prints():
        print("\n===================================" \
        "\nTest example_prints" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)

        @cache.wrapper()
        def cached_square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        for i in range(5):
            _ : int = cached_square(i)
        
        for i in range(10):
            _ : int = cached_square(i)

        # Check report
        print("\nprint():\n")
        cache.print()
        print("\nprint_cache_report:\n")
        cache.print_cache_report()
        print("\nprint_func_stats:\n")
        cache.print_func_stats(cached_square)
        print("\nprint_full_func_stats:\n")
        cache.print_full_func_stats()
        print("\nprint_full_report:\n")
        cache.print_full_report()

    def example_specific_mem_restriction():
        print("\n===================================" \
        "\nTest example_specific_mem_restriction" \
        "\n==================================="
        )

        # Make a cache bank
        cache: CacheBank = CacheBank(max_bank_size=10, lru=True)

        @cache.wrapper(max_size=CacheSize.E_128KB)
        def square(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x
        
        def cube(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x*x*x
        
        # Call wrapper
        cached_cube = cache(cube, max_size=CacheSize.E_128KB)
        
        # Square
        for i in range(5):
            _ : int = square(i)
        
        for i in range(10):
            _ : int = square(i)

        # Cube
        for i in range(5):
            _ : int = cached_cube(i)

        for i in range(10):
            _ : int = cached_cube(i)

        # Check report
        print("\nChecking Reports:\n")
        cache.print_cache_report()
        cache.print_func_stats(square)
        cache.print_func_stats(cached_cube)

    # Run Examples
    #example_init()
    #example_set_get()
    #example_set_cache_types()
    #example_cached_set_get()
    #example_many_funcs()
    #example_long_func()
    #example_save_load_pickle()
    #example_save_load_zlib()
    #example_save_load_gzip()
    #example_save_load_json()
    #example_save_load_yaml()
    #example_prints()
    #example_specific_mem_restriction()
