# Benchmark

This document provides benchmarks for various functions using caching to improve performance. The benchmarks compare the time taken to execute functions with and without caching.

## Fibonacci

```python
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
```

### Fibonacci Testing

**For calling the Fibonacci function 30 times:**

- Before caching:
  - Time taken: 0.732 seconds seconds

- After caching:
  - Time taken: 0.00001 seconds seconds
  - Cache size for `fibonacci`: 2704 bytes

- Overall improvement: 99.998% faster

**Note:** The Fibonacci function is a classic example of a recursive function that can benefit significantly from caching, as it has exponential time complexity without caching.

**For calling the Fibonacci function 35 times:**

- Before caching:
  - Time taken: 7.6236 seconds

- After caching:
  - Time taken: 0.0001 seconds
  - Cache size for `fibonacci`: 2864 bytes

- Overall improvement: 99.998% faster

**Note:** The performance improvement is even more pronounced with larger inputs due to the exponential growth of the number of recursive calls.

## Factorial

```python
def factorial(n: int) -> int:
    """Calculate the factorial of a number n."""
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
```

### Factorial Testing

**For calling the Factorial function 500 times:**

- Before caching:
  - Time taken: 0.1734 seconds

- After caching:
  - Time taken: 0.0100 seconds
  - Cache size for `factorial`: 42768 bytes

- Overall improvement: 94.24% faster

**Note:** The factorial function is another example where caching can significantly reduce the time complexity, especially for larger values of `n`.

## Sum of Squares

```python
def sum_of_squares(n: int) -> int:
    return sum(i * i for i in range(n + 1))
```

### Sum of Squares Testing

- For calling the Sum of Squares function 500 times:

- Before caching:
  - Time taken: 0.0450 seconds

- After caching:
  - Time taken: 0.0080 seconds
  - Cache size for `sum_of_squares`: 42768 bytes

- Overall improvement: 82.22% faster

**Note:** The sum of squares function benefits from caching as it avoids recalculating the sum for the same input multiple times, leading to significant performance improvements.

## Simple Time Consumption

```python
def simple_time_consumption(sleep: float) -> int:
    time.sleep(sleep)
    return 1
```

### Simple Time Consumption Testing

- For calling the Simple Time Consumption function 5 times in range 0 to 5 seconds:
- Before caching:
  - Time taken: 10.0022 seconds

- After caching:
  - Time taken: 0.0000 seconds
  - Cache size for `simple_time_consumption`: 512 bytes

- Overall improvement: 100% faster

**Note:** The simple time consumption function is a straightforward example of a function that can be cached to avoid unnecessary delays in execution, especially when the same input is used multiple times.
