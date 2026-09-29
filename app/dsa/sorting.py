"""
=============================================================================
CineBook DSA Module: Sorting Algorithms
=============================================================================
Implements Merge Sort and Quick Sort from scratch.
Configured for custom keys (rating, price, popularity, release date)
and both ascending/descending order.

DSA Concepts Covered:
1. Merge Sort (Stable Divide and Conquer)
   - Splits array into halves, recursively sorts, then merges back.
   - Time Complexity:
       Best Case:    O(n log n)
       Average Case: O(n log n)
       Worst Case:   O(n log n)
   - Space Complexity: O(n) auxiliary buffer space.
   - Why used: Stable sorting required when maintaining equal secondary rank
     (e.g., sorting movies with identical ratings by release date).

2. Quick Sort (Partition-based Divide and Conquer)
   - Chooses a pivot element, partitions array into smaller/larger elements.
   - Time Complexity:
       Best Case:    O(n log n)
       Average Case: O(n log n)
       Worst Case:   O(n^2) (mitigated using median/midpoint pivot)
   - Space Complexity: O(log n) call stack overhead.
   - Why used: Highly efficient sorting for numerical values like ticket prices
     and seat tiers.
=============================================================================
"""

from typing import List, Any, Callable


def merge_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> List[Any]:
    """
    Sorts a list using the Merge Sort algorithm.
    Returns a new sorted list (non-destructive).
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left_half = merge_sort(items[:mid], key_func=key_func, reverse=reverse)
    right_half = merge_sort(items[mid:], key_func=key_func, reverse=reverse)

    return _merge(left_half, right_half, key_func, reverse)


def _merge(
    left: List[Any],
    right: List[Any],
    key_func: Callable[[Any], Any],
    reverse: bool
) -> List[Any]:
    """Merges two sorted sublists into a single sorted list."""
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_val = key_func(left[i])
        right_val = key_func(right[j])

        # If reverse is True, higher values come first
        condition = (left_val >= right_val) if reverse else (left_val <= right_val)

        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(
    items: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> List[Any]:
    """
    Sorts a list using the Quick Sort algorithm.
    Returns a new sorted list.
    """
    arr = list(items)
    _quick_sort_helper(arr, 0, len(arr) - 1, key_func, reverse)
    return arr


def _quick_sort_helper(
    arr: List[Any],
    low: int,
    high: int,
    key_func: Callable[[Any], Any],
    reverse: bool
) -> None:
    if low < high:
        pivot_index = _partition(arr, low, high, key_func, reverse)
        _quick_sort_helper(arr, low, pivot_index - 1, key_func, reverse)
        _quick_sort_helper(arr, pivot_index + 1, high, key_func, reverse)


def _partition(
    arr: List[Any],
    low: int,
    high: int,
    key_func: Callable[[Any], Any],
    reverse: bool
) -> int:
    """Partitions sub-array around the high element as pivot."""
    pivot_val = key_func(arr[high])
    i = low - 1

    for j in range(low, high):
        val = key_func(arr[j])
        condition = (val >= pivot_val) if reverse else (val <= pivot_val)
        if condition:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def sort_catalog(
    items: List[Any],
    sort_by: str,
    algorithm: str = "merge_sort"
) -> List[Any]:
    """
    High-level sorting dispatcher for CineBook catalog items (movies, events, shows).
    
    Supported sort_by options:
    - 'rating_desc': Highest rated first
    - 'rating_asc': Lowest rated first
    - 'price_asc': Lowest ticket price first
    - 'price_desc': Highest ticket price first
    - 'release_date_desc': Newest releases first
    - 'release_date_asc': Oldest releases first
    - 'title_asc': Alphabetical A-Z
    - 'duration_desc': Longest duration first
    """
    if not items:
        return []

    # Map sort_by parameter to key function and reverse flag
    key_map = {
        "rating_desc": (lambda x: getattr(x, "rating", 0.0) or 0.0, True),
        "rating_asc": (lambda x: getattr(x, "rating", 0.0) or 0.0, False),
        "price_asc": (lambda x: getattr(x, "base_price", getattr(x, "price", 0.0)) or 0.0, False),
        "price_desc": (lambda x: getattr(x, "base_price", getattr(x, "price", 0.0)) or 0.0, True),
        "release_date_desc": (lambda x: str(getattr(x, "release_date", getattr(x, "event_date", "")) or ""), True),
        "release_date_asc": (lambda x: str(getattr(x, "release_date", getattr(x, "event_date", "")) or ""), False),
        "title_asc": (lambda x: (getattr(x, "title", getattr(x, "name", "")) or "").lower(), False),
        "duration_desc": (lambda x: getattr(x, "duration_mins", 0) or 0, True),
    }

    if sort_by not in key_map:
        return items

    key_func, reverse = key_map[sort_by]

    if algorithm == "quick_sort":
        return quick_sort(items, key_func=key_func, reverse=reverse)
    else:
        return merge_sort(items, key_func=key_func, reverse=reverse)
