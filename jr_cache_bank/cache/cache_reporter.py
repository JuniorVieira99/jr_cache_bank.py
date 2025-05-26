# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import logging

from threading import Lock
from functools import partial
from typing import Callable, Any, Dict, Optional

# Local
from jr_cache_bank.config.setup_logger import setup_logger
from jr_cache_bank.exceptions.exceptions_cache_reporter import (
    CacheReporterConstructionError,
    CacheReporterPropertyError,
    CacheReporterMagicMethodError,
    CacheReporterAddFunctionError,
    CacheReporterDellFunctionError,
    CacheReporterGetFunctionError,
    CacheReporterSetFunctionError,
    CacheReporterUtilsError
)

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


class CacheReporter:
    """
    CacheReporter
    =============
    A class that implements a cache reporter for reporting the status of the cache bank.
    It keeps track of the number of hits, misses, and hit/miss rates for each function in the cache bank.

    Notes:
    -----
        - The cache reporter is thread-safe and can be used in a multi-threaded environment.

    Attributes:
        total (int) :
            The total number of cache accesses.
        hits (int) :
            The total number of cache hits.
        misses (int) :
            The total number of cache misses.
        hit_rate (float) :
            The hit rate of the cache.
        miss_rate (float) :
            The miss rate of the cache.
        funcs (Dict[str, Dict[str, Any]]) :
            A dictionary containing the functions used in the cache.

    Methods:
    ---------
        ### add_func(func: Callable | partial) :
            Adds a function to the cache reporter.
        ### del_func(func: Callable | partial) :
            Deletes a function from the cache reporter.
        ### set_hit(func: str | Callable | partial) :
            Sets the hit for a function in the cache reporter.
        ### set_miss(func: str | Callable | partial) :
            Sets the miss for a function in the cache reporter.
        ### get(func: str | Callable | partial) :
            Returns the value associated with the function in the cache reporter.
        ### set(func: str | Callable | partial, value: Dict[str, Any]) :
            Sets the value associated with the function in the cache reporter.
        ### clear() :
            Clears the cache reporter.
        ### is_empty() :
            Returns True if the cache reporter is empty, False otherwise.
        ### print_func_report(func: Callable | partial | str) :
            Prints the report for a function in the cache reporter.
        ### print_full_func_reports() :
            Prints the full report for all functions in the cache reporter.
        ### print_report() :
            Prints the report for the cache reporter.
    """

    # -------------
    # Slots

    __slots__ = (
        "_total",
        "_hits",
        "_misses",
        "_hit_rate",
        "_miss_rate",
        "_funcs",
        "_mutex"
    )

    # -------------
    # Attributes

    _total: int
    _hits: int
    _misses: int
    _hit_rate: float
    _miss_rate: float
    _funcs: Dict[str, Dict[str, Any]]
    _mutex: Optional[Lock]

    # -------------
    # Constructor

    def __init__(self) -> None:
        """
        __init__
        ======
        Constructor for the CacheReporter class.
        """
        try:
            super().__init__()
            self.hits = 0
            self.misses = 0
            self.hit_rate = 0.0
            self.miss_rate = 0.0
            self.funcs = {}
            self._mutex = None
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> initializing cache reporter: {e}")
            raise CacheReporterConstructionError(
                f"Error '{e.__class__.__name__}' -> initializing cache reporter: \n\t{e}"
            ) from e

    # -------------
    # Properties

    @property
    def total(self) -> int:
        """
        Returns the total number of cache accesses.
        """
        try:
            self._total = self.hits + self.misses
            if self._total == 0:
                self._hit_rate = 0.0
                self._miss_rate = 0.0
            else:
                self._hit_rate = self.hits / self._total
                self._miss_rate = self.misses / self._total
            return self._total
        except Exception as e:
            LOGGER.error(f"Error getting 'total' from cache reporter: {e}")
            raise CacheReporterPropertyError(
                "Error getting 'total' from cache reporter."
            ) from e
    
    @property
    def hits(self) -> int:
        """
        Returns the total number of cache hits.
        """
        return self._hits
    
    @property
    def misses(self) -> int:
        """
        Returns the total number of cache misses.
        """
        return self._misses
    
    @property
    def hit_rate(self) -> float:
        """
        Returns the hit rate of the cache.
        """
        try:
            if self._total == 0:
                self._hit_rate = 0.0
            else:
                self._hit_rate = self.hits / self._total
            if self._hit_rate < 0.0 or self._hit_rate > 1.0:
                raise ValueError("Hit rate must be between 0.0 and 1.0.")
            return self._hit_rate
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting 'hit_rate' from cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> getting 'hit_rate' from cache reporter: {e}"
            ) from e

    @property
    def miss_rate(self) -> float:
        """
        Returns the miss rate of the cache.
        """
        try:
            if self._total == 0:
                self._miss_rate = 0.0
            else:
                self._miss_rate = self.misses / self._total
            if self._miss_rate < 0.0 or self._miss_rate > 1.0:
                raise ValueError("Miss rate must be between 0.0 and 1.0.")
            return self._miss_rate
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting 'miss_rate' from cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> getting 'miss_rate' from cache reporter: {e}"
            ) from e

    @property
    def funcs(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the functions used in the cache.
        """
        return self._funcs
    
    @property
    def mutex(self) -> Lock:
        """
        Returns the mutex used for thread safety.
        """
        if self._mutex is None:
            self._mutex = Lock()
        return self._mutex

    # -------------
    # Setters

    @hits.setter
    def hits(self, value: int) -> None:
        """
        Sets the total number of cache hits.
        """
        try:
            if not isinstance(value, int):
                raise TypeError("Hits must be an integer.")
            if value < 0:
                raise ValueError("Hits must be greater than or equal to 0.")
            self._hits = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting 'hits' in cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> setting 'hits' in cache reporter: {e}"
            ) from e

    @misses.setter
    def misses(self, value: int) -> None:
        """
        Sets the total number of cache misses.
        """
        try:
            if not isinstance(value, int):
                raise TypeError("Misses must be an integer.")
            if value < 0:
                raise ValueError("Misses must be greater than or equal to 0.")
            self._misses = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting 'misses' in cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> setting 'misses' in cache reporter: {e}"
            ) from e
        
    @hit_rate.setter
    def hit_rate(self, value: float) -> None:
        """
        Sets the hit rate of the cache.
        """
        try:
            if not isinstance(value, float):
                raise TypeError("Hit rate must be a float.")
            if value < 0.0 or value > 1.0:
                raise ValueError("Hit rate must be between 0.0 and 1.0.")
            self._hit_rate = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting 'hit_rate' in cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> setting 'hit_rate' in cache reporter: {e}"
            ) from e
    
    @miss_rate.setter
    def miss_rate(self, value: float) -> None:
        """
        Sets the miss rate of the cache.
        """
        try:
            if not isinstance(value, float):
                raise TypeError("Miss rate must be a float.")
            if value < 0.0 or value > 1.0:
                raise ValueError("Miss rate must be between 0.0 and 1.0.")
            self._miss_rate = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting 'miss_rate' in cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> setting 'miss_rate' in cache reporter: {e}"
            ) from e

    @funcs.setter
    def funcs(self, value: Dict[str, Dict[str, Any]]) -> None:
        """
        Sets the functions used in the cache.
        """
        try:
            if not isinstance(value, dict):
                raise TypeError("Functions must be a dictionary.")
            self._funcs = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting 'funcs' in cache reporter: {e}")
            raise CacheReporterPropertyError(
                f"Error '{e.__class__.__name__}' -> setting 'funcs' in cache reporter: {e}"
            ) from e

    # -------------
    # Magic Methods

    def __str__(self) -> str:
        """
        Returns a string representation of the cache reporter.
        """
        return f"CacheReporter(total={self.total}, hits={self.hits}, misses={self.misses}, hit_rate={self.hit_rate}, miss_rate={self.miss_rate})"

    def __len__(self) -> int:
        """
        Returns the number of items in the cache reporter.
        """
        return len(self.funcs)

    def __contains__(self, key: str) -> bool:
        """
        Returns True if the key is in the cache reporter, False otherwise.
        """
        try:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            return key in self.funcs
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> checking if key is in cache reporter: {e}")
            raise CacheReporterMagicMethodError(
                f"Error '{e.__class__.__name__}' -> checking if key is in cache reporter: {e}"
            ) from e
        
    def __getitem__(self, key: str) -> Dict[str, Any]:
        """
        Returns the value associated with the key in the cache reporter.
        """
        try:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            if key in self.funcs:
                return self.funcs[key]
            else:
                raise KeyError(f"Key {key} not found in cache reporter.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting item from cache reporter: {e}")
            raise CacheReporterMagicMethodError(
                f"Error '{e.__class__.__name__}' -> getting item from cache reporter: {e}"
            ) from e
        
    def __setitem__(self, key: str, value: Dict[str, Any]) -> None:
        """
        Sets the value associated with the key in the cache reporter.
        """
        try:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            if key in self.funcs:
                LOGGER.warning(f"Key {key} already exists in cache reporter.")
            if not isinstance(value, dict):
                raise TypeError("Value must be a dictionary.")
            self.funcs[key] = value
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting item in cache reporter: {e}")
            raise CacheReporterMagicMethodError(
                f"Error '{e.__class__.__name__}' -> setting item in cache reporter: {e}"
            ) from e
        
    def __delitem__(self, key: str) -> None:
        """
        Deletes the item associated with the key in the cache reporter.
        """
        try:
            if not isinstance(key, str):
                raise TypeError("Key must be a string.")
            if key in self.funcs:
                del self.funcs[key]
            else:
                raise KeyError(f"Key {key} not found in cache reporter.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> deleting item from cache reporter: {e}")
            raise CacheReporterMagicMethodError(
                f"Error '{e.__class__.__name__}' -> deleting item from cache reporter: {e}"
            ) from e

    # -------------
    # Methods

    def add_func(self, func: Callable | partial) -> None:
        """
        add_func
        ========
        Adds a function to the cache reporter.

        Arguments:
            func (Callable) :
                The function to add to the cache reporter.
        """
        try:
            # Get the function name
            func_name: str = self._extract_name(func)

            if func_name in self.funcs:
                return
            
            with self.mutex:
                self.funcs[func_name] = {}
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> adding function to cache reporter: {e}")
            raise CacheReporterAddFunctionError(
                f"Error '{e.__class__.__name__}' -> adding function to cache reporter: {e}"
            ) from e
    
    def del_func(self, func: Callable | partial) -> None:
        """
        del_func
        ========
        Deletes a function from the cache reporter.

        Arguments:
            func (Callable | partial) :
                The function to delete from the cache reporter.
        """
        try:
            # Get the function name
            func_name: str = self._extract_name(func)

            if func_name not in self.funcs:
                return
            
            with self.mutex:
                del self.funcs[func_name]
            
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> deleting function from cache reporter: {e}")
            raise CacheReporterDellFunctionError(
                f"Error '{e.__class__.__name__}' -> deleting function from cache reporter: {e}"
            ) from e

    def set_hit(self, func: str | Callable | partial) -> None:
        """
        set_hit
        =======
        Sets the hit for a function in the cache reporter.

        Arguments:
            func (str | Callable | partial) :
                The function to set the hit for.
        """
        try:
            # Get the function name
            func_name: str = self._extract_name(func)

            if func in self.funcs:
                with self.mutex:
                    self.funcs[func_name]["hits"] = self.funcs[func_name].setdefault("hits", 0) + 1
                    self.funcs[func_name]["total"] = self.funcs[func_name].setdefault("total", 0) + 1
                    self.hits += 1

                    # Calculate rate
                    if self.funcs[func_name]["total"] > 0:
                        hit_rate: float = self.funcs[func_name]["hits"] / self.funcs[func_name]["total"]
                    else:
                        hit_rate: float = 0.0

                    # Update the hit rate
                    self.funcs[func_name]["hit_rate"] = hit_rate

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting hit for function in cache reporter: {e}")
            raise CacheReporterSetFunctionError(
                f"Error '{e.__class__.__name__}' -> setting hit for function in cache reporter: {e}"
            ) from e

    def set_miss(self, func: str | Callable | partial) -> None:
        """
        set_miss
        ========
        Sets the miss for a function in the cache reporter.

        Arguments:
            func (Callable) :
                The function to set the miss for.
        """
        try:
            # Get the function name
            func_name: str = self._extract_name(func)

            if func_name in self.funcs:
                with self.mutex:
                    self.funcs[func_name]["misses"] = self.funcs[func_name].setdefault("misses", 0) + 1
                    self.funcs[func_name]["total"] = self.funcs[func_name].setdefault("total", 0) + 1
                    self.misses += 1

                    # Calculate rate
                    if self.funcs[func_name]["total"] > 0:
                        miss_rate: float = self.funcs[func_name]["misses"] / self.funcs[func_name]["total"]
                    else:
                        miss_rate: float = 0.0

                    # Update the miss rate
                    self.funcs[func_name]["miss_rate"] = miss_rate

        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting miss for function in cache reporter: {e}")
            raise CacheReporterSetFunctionError(
                f"Error '{e.__class__.__name__}' -> setting miss for function in cache reporter: {e}"
            ) from e

    def get(self, func: str | Callable | partial) -> Dict[str, Any] | None:
        """
        get
        ====
        Returns the value associated with the function in the cache reporter.

        Arguments:
            func (str | Callable | partial)) :
                The function to get the value for.
        
        Returns:
            Dict[str, Any] | None:
                - The value associated with the function in the cache reporter.
                - None if the function is not found in the cache reporter.
        """
        try:
            # Get the function name
            func_name: str = self._extract_name(func)

            if not isinstance(func_name, str):
                raise TypeError("Key must be a string.")
            
            if func_name in self.funcs:
                with self.mutex:
                    return self.funcs[func_name]
            else:
                LOGGER.warning(f"Function {func_name} not found in cache reporter.")
                return None
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> getting item from cache reporter: {e}")
            raise CacheReporterGetFunctionError(
                f"Error '{e.__class__.__name__}' -> getting item from cache reporter: {e}"
            ) from e
        
    def set(self, func: str | Callable | partial, value: Dict[str, Any]) -> None:
        """
        set
        ===
        Sets the value associated with the function in the cache reporter.

        Arguments:
            func (str | Callable | partial) :
                The function to set the value for.
            value (Dict[str, Any]) :
                The value to set for the function.
        """
        try:
            # Get the function name
            func_name: str = self._extract_name(func)

            if func_name in self.funcs:
                with self.mutex:
                    self.funcs[func_name] = value
            else:
                raise KeyError(f"Function {func_name} not found in cache reporter.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> setting item in cache reporter: {e}")
            raise CacheReporterSetFunctionError(
                f"Error '{e.__class__.__name__}' -> setting item in cache reporter: {e}"
            ) from e

    def clear(self) -> None:
        """
        clear
        ======
        Clears the cache reporter.
        """
        try:
            with self.mutex:
                self.funcs.clear()
                self.hits = 0
                self.misses = 0
                self.hit_rate = 0.0
                self.miss_rate = 0.0
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> clearing cache reporter: {e}")
            raise CacheReporterMagicMethodError(
                f"Error '{e.__class__.__name__}' -> clearing cache reporter: {e}"
            ) from e

    # -------------
    # Utils

    def is_empty(self) -> bool:
        """
        is_empty
        ========
        Returns True if the cache reporter is empty, False otherwise.
        """
        return len(self.funcs) == 0
        
    def print_func_report(self, func: Callable | partial| str) -> None:
        """
        print_func_report
        =================
        Prints the report for a function in the cache reporter.

        Arguments:
            func (Callable) :
                The function to print the report for.
        """
        try:
            if isinstance(func, partial):
                func_name:str = func.func.__name__
            elif callable(func):
                func_name:str = func.__name__
            else:
                raise TypeError("Function must be callable or partial.")
            
            if func in self.funcs:
                with self.mutex:
                    string: str = f"Function {func_name}:\n"
                    for key, value in self.funcs[func_name].items():
                        string += f"{key}: {value}\n"
                print(string)
            else:
                LOGGER.warning(f"Function {func_name} not found in cache reporter.")
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing function report: {e}")
            raise CacheReporterMagicMethodError(
                f"Error '{e.__class__.__name__}' -> printing function report: {e}"
            ) from e

    def print_full_func_reports(self) -> None:
        """
        print_full_func_reports
        =======================
        Prints the full report for all functions in the cache reporter.
        """
        try:
            string: str = "Full Function Reports:\n"
            string += f"Total: {self.total}\n"
            string += f"Hits: {self.hits}\n"
            string += f"Misses: {self.misses}\n"
            string += f"Hit Rate: {self.hit_rate:.2f}\n"
            string += f"Miss Rate: {self.miss_rate:.2f}\n"
            string += "Functions:\n"

            with self.mutex:
                for key, value in self.funcs.items():
                    string += f"\t{key}:\n"
                    for k, v in value.items():
                        string += f"\t{k}: {v}\n"
            print(string)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing full function reports: {e}")
            raise CacheReporterUtilsError(
                f"Error '{e.__class__.__name__}' -> printing full function reports: {e}"
            ) from e
            
    def print_report(self) -> None:
        """
        print_report
        ============
        Prints the report for the cache reporter.
        """
        try:
            string: str = "Cache Reporter:\n"
            string += f"Total: {self.total}\n"
            string += f"Hits: {self.hits}\n"
            string += f"Misses: {self.misses}\n"
            string += f"Hit Rate: {self.hit_rate:.2f}\n"
            string += f"Miss Rate: {self.miss_rate:.2f}\n"
            string += "Functions:\n"

            with self.mutex:
                for key, _ in self.funcs.items():
                    string += f"\t{key}\n"

            print(string)
        except Exception as e:
            LOGGER.error(f"Error '{e.__class__.__name__}' -> printing report: {e}")
            raise CacheReporterUtilsError(
                f"Error '{e.__class__.__name__}' -> printing report: {e}"
            ) from e

    # -------------
    # Helpers

    def _extract_name(self, func: str | Callable | partial) -> str:
        """
        _extract_name
        =============
        Extracts the name of the function from a callable or partial.

        Arguments:
            func (str | Callable | partial) :
                The function to extract the name from.
        
        Returns:
            str :
                The name of the function.
        """
        if isinstance(func, str):
            return func
        elif isinstance(func, partial):
            return func.func.__name__
        elif callable(func):
            return func.__name__
        else:
            raise TypeError("Function must be callable or partial.")
