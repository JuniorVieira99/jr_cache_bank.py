# jr_cache_bank - version 0.1.0

A simple, flexible, and thread-safe caching library for Python applications that provides multiple caching strategies and detailed cache performance reporting.

This library is designed to be easy to use, with a simple API that allows you to cache the results of expensive function calls and retrieve them later without recomputing.

------------------------

## Index

- [Features](#features)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Basic Usage with Decorators](#basic-usage-with-decorators)
  - [Manual Caching](#manual-caching)
  - [Using Different Cache Types](#using-different-cache-types)
  - [Cache Printing Methods](#cache-printing-methods)
- [Enums](#enums)
  - [CacheType](#cachetype)
  - [CacheSize](#cachesize)
- [API Reference](#api-reference)
  - [CacheBank](#cachebank)
  - [CacheBank Methods](#cachebank-methods)
  - [Cache Usage Methods](#cache-usage-methods)
  - [Cache Bank Utils](#cache-bank-utils)
  - [Cache Persistence](#cache-persistence)
  - [Cache Performance Monitoring](#cache-performance-monitoring)
- [Tests](#tests)
- [License](#license)
- [Contributions](#contributions)

------------------------

## Features

- 🔒 Thread-safe and process-safe caching
- 🚀 Simple API with function decorators for easy implementation
- 🔄 Multiple cache types (pickle, zlib, gzip, JSON, YAML) for flexibility
- 📊 Detailed cache reporting for performance monitoring
- 💾 Persistence with save/load capabilities
- ⏱️ LRU (Least Recently Used) eviction policy
- 🛠️ Configurable maximum size, compression level, and more
- Robust memory management with size limits per-function, total memory size, and maximum bank size
- 🧪 Comprehensive tests for functionality and performance

------------------------

## Dependencies

- `pyaml` - For YAML serialization
- `pytest` - For testing, if necessary

## Installation

Requires Python 3.12+

```bash
pip install jr_cache_bank
```

------------------------

## Quick Start

```python
from jr_cache_bank import CacheBank, CacheType

# Create a cache bank
cache_bank = CacheBank(max_bank_size=100, lru=True)

# Use as a decorator
@cache_bank.wrapper()
def expensive_function(x):
    # Expensive computation here
    return x * x

# Call the function - first time will compute and cache
result1 = expensive_function(42)

# Call again - will retrieve from cache
result2 = expensive_function(42)

# Print cache statistics
cache_bank.print_cache_report()
```

------------------------

## Usage Examples

### Basic Usage with Decorators

```python
from jr_cache_bank import CacheBank

# Create a cache bank
cache = CacheBank()

@cache.wrapper()
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# First execution will compute and cache results
result = fibonacci(30)
print(result)  # Output: 832040
# Second execution will retrieve from cache, and immediately return
result = fibonacci(30)
print(result)  # Output: 832040
```

### Usage with Decorators and Maximum Memory Size

```python
from jr_cache_bank import CacheBank, CacheSize

# Create a cache bank
cache = CacheBank()

# Create a cache bank with a maximum memory size for the func cached
# Otherwiise, will use the default max_func_memory_size attribute
@cache.wrapper(max_size=CacheSize.E_1MB) # Enum for cache size - 1mb
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Using Call Functions

```python
from jr_cache_bank import CacheBank

# Create a cache bank
cache = CacheBank()

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Cache function using call
wrapped_fibonacci = cache(fibonacci)
# Cache function using call and memory restriction
wrapped_fibonacci = cache(fibonacci, max_size=CacheSize.E_1MB)
```

### Manual Caching

```python
from jr_cache_bank import CacheBank

# Create a cache bank
cache = CacheBank()

def square(x):
    return x * x

# Manually cache results
for i in range(5):
    result = square(i)
    cache.set(square, args=(i,), kwargs={}, result=result)

# Retrieve from cache
cached_result = cache.get(square, args=(3,), kwargs={})
print(cached_result)  # Output: 9
```

### Using Different Cache Types

```python
from jr_cache_bank import CacheBank, CacheType

# Create a cache bank with gzip compression
cache = CacheBank(cache_type=CacheType.GZIP)

@cache.wrapper()
def expensive_function(x, y):
    # Expensive computation here
    return x * y

# Save the cache to a file
cache.save("my_cache.gz")

# Load the cache from a file
cache.load("my_cache.gz")
```

### Cache Printing Methods

```python
from jr_cache_bank import CacheBank

# Create a cache bank
cache = CacheBank()

@cache.wrapper()
def compute_function(x):
    return x * x

# Use the function multiple times
for i in range(10):
    compute_function(i % 5)  # Will cause some cache hits

# Print cache statistics
cache.print_cache_report()
# Print detailed function statistics
cache.print_func_stats(compute_function)
# Print all function statistics
cache.print_all_func_stats()
```

------------------------

## Enums

### CacheType

Enum for different cache serialization strategies:

- `CacheType.PICKLE` - Standard Python serialization
- `CacheType.ZLIB` - Compressed serialization with zlib
- `CacheType.GZIP` - Compressed serialization with gzip
- `CacheType.JSON` - Serialization to JSON format
- `CacheType.YAML` - Serialization to YAML format

### CacheSize

Enum for different cache sizes, should used as a integer:

- `CacheSize.E_1KB` - 1 KB
- `CacheSize.E_2KB` - 2 KB
- `CacheSize.E_4KB` - 4 KB
- `CacheSize.E_8KB` - 8 KB
- `CacheSize.E_16KB` - 16 KB
- `CacheSize.E_32KB` - 32 KB
- `CacheSize.E_64KB` - 64 KB
- `CacheSize.E_128KB` - 128 KB
- `CacheSize.E_256KB` - 256 KB
- `CacheSize.E_512KB` - 512 KB
- `CacheSize.E_1MB` - 1 MB
- `CacheSize.E_2MB` - 2 MB
- `CacheSize.E_4MB` - 4 MB
- `CacheSize.E_8MB` - 8 MB
- `CacheSize.E_16MB` - 16 MB
- `CacheSize.E_32MB` - 32 MB

------------------------

## API Reference

### CacheBank

The main class for creating and managing caches.

```python
CacheBank(
    max_bank_size=100,                              # Maximum number of functions to cache
    max_total_memory_size= CacheSize.E_10MB,        # Maximum total memory size for all caches
    max_func_memory_size=CacheSize.E_16KB,          # Maximum memory size for each function cache
    lru=True,                                       # Use Least Recently Used eviction
    max_file_size=100000,                           # Maximum file size for saved cache
    cache_type=CacheType.PICKLE,                    # Cache serialization type
    cache_bank = OrderedDict(),                     # Cache bank for storing function caches
    filename=None                                   # File to save/load cache
)
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| max_bank_size | int | Maximum number of functions to cache. |
| max_total_memory_size | (CacheSize, int) | Maximum total memory size for all caches. |
| max_func_memory_size | (CacheSize, int) | Maximum memory size for each function cache. |
| lru | bool | Use Least Recently Used eviction policy. |
| max_file_size | int | Maximum file size for saved cache. |
| cache_type | CacheType | Cache serialization type. |
| cache_bank | OrderedDict | Cache bank for storing function caches. |
| filename | (str, None) | File to save/load cache. |

**Example:**

```python
# import the library
from jr_cache_bank import CacheBank, CacheType
# Create a cache bank
cache = CacheBank(
    max_bank_size=100, 
    cache_type=CacheType.ZLIB, 
    max_total_memory_size=CacheSize.E_1MB,
    max_func_memory_size=CacheSize.E_8KB,
)
```

------------------------

### CacheBank Methods

**Cache Usage Methods:**

| Method | Description |
|--------|-------------|
| `get` | Retrieve a cached result for a given function and its arguments. |
| `set` | Store a result in the cache for a given function and its arguments. |
| `clear` | Clear all caches in the cache bank. |
| `remove` | Remove a specific function's cache from the cache bank. |
| `items` | Retrieve all items in the cache bank. |
| `keys` | Retrieve all keys (functions) in the cache bank. |
| `values` | Retrieve all values (caches) in the cache bank. |
| `wrapper` | Wrap a function with caching capabilities. |

**Cache Bank Utils:**

| Method | Description |
|--------|-------------|
| `is_full` | Check if the cache bank is full. |
| `is_empty` | Check if the cache bank is empty. |
| `is_cache_report_empty` | Check if the cache report is empty. |

**Cache Persistence:**

| Method | Description |
|--------|-------------|
| `save` | Save the cache bank to a file. |
| `load` | Load the cache bank from a file. |

**Cache Performance Monitoring:**

| Method | Description |
|--------|-------------|
| `print` | Print a report on the cache bank's performance. |
| `print_cache_report` | Print a report on the cache bank's performance. |
| `print_func_stats` | Print statistics for a specific cached function. |
| `print_all_func_stats` | Print statistics for all cached functions. |

------------------------

### Cache Usage Methods

#### get

**Signature:**

```python
def get(self, func: Callable, args: tuple, kwargs: dict) -> Any:
```

Retrieve a cached result for a given function and its arguments.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| func | Callable | The function to retrieve the cached result for. |
| args | tuple | The positional arguments used to call the function. |
| kwargs | dict | The keyword arguments used to call the function. |

**Returns:**

- `Any`: The cached result if found, otherwise `None`.

**Example:**

```python
# Retrieve a cached result
result = cache.get(expensive_function, args=(42,), kwargs={})
print(result)  # Output: 1764 (if cached)
```

#### set

**Signature:**

```python
def set(self, func: Callable, args: tuple, kwargs: dict, result: Any) -> None:
```

Store a result in the cache for a given function and its arguments.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| func | Callable | The function to store the result for. |
| args | tuple | The positional arguments used to call the function. |
| kwargs | dict | The keyword arguments used to call the function. |
| result | Any | The result to store in the cache. |

**Returns:**

- `None`

**Example:**

```python
# Store a result in the cache
cache.set(expensive_function, args=(42,), kwargs={}, result=1764)
```

#### clear

**Signature:**

```python
def clear(self) -> None:
```

Clear all caches in the cache bank.

**Returns:**

- `None`

**Example:**

```python
# Clear all caches
cache.clear()
```

#### remove

**Signature:**

```python
def remove(self, func: Callable) -> None:
```

Remove a specific function's cache from the cache bank.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| func | Callable | The function whose cache to remove. |

**Returns:**

- `None`

**Example:**

```python
# Remove a specific function's cache
cache.remove(expensive_function)
```

#### items

**Signature:**

```python
def items(self) -> List[Tuple[Any, Any]]:
```

Retrieve all items in the cache bank.

**Returns:**

- `List[Tuple[Any, Any]]`: A list of tuples containing the function and its cache.

**Example:**

```python
# Retrieve all items in the cache bank
items = cache.items()
```

#### keys

**Signature:**

```python
def keys(self) -> List[Any]:
```

Retrieve all keys (functions) in the cache bank.

**Returns:**

- `List[Any]`: A list of functions in the cache bank.

**Example:**

```python
# Retrieve all keys in the cache bank
keys = cache.keys()
```

#### values

**Signature:**

```python
def values(self) -> List[Any]:
```

Retrieve all values (caches) in the cache bank.

**Returns:**

- `List[Any]`: A list of caches in the cache bank.

**Example:**

```python
# Retrieve all values in the cache bank
values = cache.values()
```

#### wrapper

**Signature:**

```python
def wrapper(self, func: Callable, max_size: Optional[CacheSize] = None) -> Callable:
```

Wrap a function with caching capabilities.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| func | Callable | The function to wrap with caching. |
| max_size | Optional[CacheSize] | The maximum size of the cache for this function. If None, uses the default size. |

**Returns:**

- `Callable`: The wrapped function with caching capabilities.

**Example:**

```python
# Wrap a function with caching
@cache.wrapper()
def expensive_function(x):
    return x * x

# Wrap a function with specific max memory size
@cache.wrapper(max_size=CacheSize.E_1MB)
def expensive_function(x):
    return x * x
```

#### call

**Signature:**

```python
def __call__(self, func: Callable, max_size: Optional[CacheSize] = None) -> Callable:
```

Wrap a function with caching capabilities.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| func | Callable | The function to wrap with caching. |
| max_size | Optional[CacheSize] | The maximum size of the cache for this function. If None, uses the default size. |

**Returns:**

- `Callable`: The wrapped function with caching capabilities.

**Example:**

```python
cache = CacheBank()
# Wrap a function with caching
wrapped_function = cache(expensive_function, max_size=CacheSize.E_1MB)
```

------------------------

### Cache Bank Utils

#### is_full

**Signature:**

```python
def is_full(self) -> bool:
```

Check if the cache bank is full.

**Returns:**

- `bool`: `True` if the cache bank is full, otherwise `False`.

**Example:**

```python
# Check if the cache bank is full
is_full = cache.is_full()
print(is_full)  # Output: True or False
```

#### is_empty

**Signature:**

```python
def is_empty(self) -> bool:
```

Check if the cache bank is empty.

**Returns:**

- `bool`: `True` if the cache bank is empty, otherwise `False`.

**Example:**

```python
# Check if the cache bank is empty
is_empty = cache.is_empty()
print(is_empty)  # Output: True or False
```

#### is_cache_report_empty

**Signature:**

```python
def is_cache_report_empty(self) -> bool:
```

Check if the cache report is empty.

**Returns:**

- `bool`: `True` if the cache report is empty, otherwise `False`.

**Example:**

```python
# Check if the cache report is empty
is_cache_report_empty = cache.is_cache_report_empty()
print(is_cache_report_empty)  # Output: True or False
```

------------------------

### Cache Persistence

The cache bank provides methods to save and load the cache to and from a file.

### Default paths to save and load cache

- The standard paths are:
  - ../cache/dump/cache_bank.pkl
  - ../cache/dump/cache_bank.zlib
  - ../cache/dump/cache_bank.gz
  - ../cache/dump/cache_bank.json
  - ../cache/dump/cache_bank.yaml

#### save

**Signature:**

```python
def save(self, filename: Optional[str] = None) -> None:
```

Save the cache bank to a file.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| filename | Optional[str] | The name of the file to save the cache to. If None, uses the filename provided at initialization. |

**Returns:**

- `None`

**Example:**

```python
# Save the cache to a file
cache.save("my_cache.pkl")
```

#### load

**Signature:**

```python
def load(self, filename: Optional[str] = None):
```

Load the cache bank from a file.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| filename | Optional[str] | The name of the file to load the cache from. If None, uses the filename provided at initialization. |

**Returns:**

- `None`

**Example:**

```python
# Load the cache from a file
cache.load("my_cache.pkl")
```

------------------------

### Cache Performance Monitoring

The cache bank provides methods to monitor the performance of cached functions.

#### print

**Signature:**

```python
def print(self) -> None:
```

Print all the cache bank's cached functions.

**Returns:**

- `None`

**Example:**

```python
# Print all cached functions
cache.print()
```

**Output:**

```bash
Cache Bank:
cached_square: OrderedDict({('cached_square', (0,)): 0, ('cached_square', (1,)): 1, ('cached_square', (2,)): 4, ('cached_square', (3,)): 9, ('cached_square', (4,)): 16, ('cached_square', (5,)): 25, ('cached_square', (6,)): 36, ('cached_square', (7,)): 49, ('cached_square', (8,)): 64, ('cached_square', (9,)): 81})
```

#### print_cache_report

**Signature:**

```python
def print_cache_report(self) -> None:
```

Print a report on the cache bank's performance.

**Returns:**

- `None`

**Example:**

```python
# Print the cache report
cache.print_cache_report()
```

**Output:**

```bash
Cache Reporter:      
Total: 14
Hits: 5
Misses: 9
Hit Rate: 0.36       
Miss Rate: 0.64      
Functions:
        cached_square
```

#### print_func_stats

**Signature:**

```python
def print_func_stats(self, func: Callable) -> None:
```

Print statistics for a specific cached function.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| func | Callable | The function to print statistics for. |

**Returns:**

- `None`

**Example:**

```python
# Print function statistics
cache.print_func_stats(expensive_function)
```

**Output:**

```bash
Full Function Reports:
Total: 14
Hits: 5
Misses: 9
Hit Rate: 0.36
Miss Rate: 0.64
Functions:
        expensive_function:
        misses: 9
        total: 14
        miss_rate: 0.6428571428571429
        hits: 5
        hit_rate: 0.5555555555555556
```

#### print_all_func_stats

**Signature:**

```python
def print_all_func_stats(self) -> None:
```

Print statistics for all cached functions.

**Returns:**

- `None`

**Example:**

```python
# Print all function statistics
cache.print_all_func_stats()
```

**Output:**

```bash
Cache Bank Report:
Max Bank Size: 10
LRU: True
Cache Bank Length: 1
Cache Bank:
        cached_square: OrderedDict({('cached_square', (0,)): 0, ('cached_square', (1,)): 1, ('cached_square', (2,)): 4, ('cached_square', (3,)): 9, ('cached_square', (4,)): 16, ('cached_square', (5,)): 25, ('cached_square', (6,)): 36, ('cached_square', (7,)): 49, ('cached_square', (8,)): 64, ('cached_square', (9,)): 81})
```

------------------------

## Tests

Tests are located in the `tests` directory. You can run them using `pytest`:

- To run functionality tests:

```bash
pytest tests/test_cache_bank.py
```

- To run performance tests:

```bash
pytest tests/test_cache_bank_bench.py
```

- To run lru tests:

```bash
pytest tests/test_cache_bank_lru.py
```

------------------------

## License

MIT License

------------------------

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.
