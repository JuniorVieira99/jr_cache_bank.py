# Usage Examples

## CacheBank default values

```python
my_cache = CacheBank(
    max_bank_size: int = 100,
    max_total_memory_size: int = CacheSize.E_10MB,
    max_func_memory_size: int = CacheSize.E_16KB,
    lru: bool = True,
    max_file_size: int = CacheSize.E_10MB,
    cache_type: CacheType = CacheType.PICKLE,
    cache_bank: Optional[OrderedDict[str, OrderedDict[Tuple, Any]]] = None,
    func_size_dict: Optional[Dict[str, CacheSize]] = None,
    filename: Optional[Union[str, Path]] = None
)
```

## Initialization with specific parameters

```python
# import the cache module
from jr_cache_bank import CacheBank, CacheSize

# create a cache bank instance - Initializes with default settings
my_cache = CacheBank()

# create a cache bank instance with specific parameters
my_cache = CacheBank(
    max_bank_size: int = 100,
    max_total_memory_size: int = CacheSize.E_10MB,
    max_func_memory_size: int = CacheSize.E_16KB,
    lru: bool = True,
    max_file_size: int = CacheSize.E_10MB,
    cache_type: CacheType = CacheType.PICKLE,
    cache_bank: Optional[OrderedDict[str, OrderedDict[Tuple, Any]]] = None,
    func_size_dict: Optional[Dict[str, CacheSize]] = None,
    filename: Optional[Union[str, Path]] = None
)
```

## Basic Usage

```python
# import the cache module
from jr_cache_bank import CacheBank
# create a cache bank instance - Initializes with default settings
my_cache = CacheBank() 

# Wrapping a function to cache its results
@my_cache.wrapper()
def expensive_computation(x):
    # Simulate an expensive computation
    return x * x

# Call the function
result = expensive_computation(10)
print(result)  # Output: 100

# Get the cached result directly if necessary
cached_result = my_cache.get(expensive_computation, args=(10,))
```

## Manual Usage

```python
# import the cache module
from jr_cache_bank import CacheBank

# create a cache bank instance - Initializes with default settings
my_cache = CacheBank()

# Some function to cache
def expensive_computation(x):
    return x * x

# Manually cache the result
my_cache.set(expensive_computation, args=(10,), value=100)
# Retrieve the cached result
cached_result = my_cache.get(expensive_computation, args=(10,))
print(cached_result)  # Output: 100
```

## Use with call

```python
# import the cache module
from jr_cache_bank import CacheBank

# create a cache bank instance - Initializes with default settings
my_cache = CacheBank()

# Some function to cache
def expensive_computation(x):
    return x * x

# wrap the func with call
wrapped_func = my_cache(expensive_computation)

# Call the wrapped function
wrapped_func(10)

# Retrieve the cached result
cached_result = my_cache.get(expensive_computation, args=(10,))
print(cached_result)  # Output: 100
```

## Use with specify function memory size

```python
# import the cache module
from jr_cache_bank import CacheBank

# create a cache bank instance - Initializes with default settings
my_cache = CacheBank()

# Some function to cache
def expensive_computation(x):
    return x * x

# wrap the func with call and specify memory size
wrapped_func = my_cache(expensive_computation, max_size=CacheSize.E_128KB)

# Call the wrapped function
wrapped_func(10)

# Retrieve the cached result
cached_result = my_cache.get(expensive_computation, args=(10,))
print(cached_result)  # Output: 100
```
