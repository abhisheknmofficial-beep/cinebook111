"""
=============================================================================
CineBook DSA Module: Searching Algorithms
=============================================================================
Contains implementations of Linear Search and Binary Search tailored for
movie, event, and show lookups.

DSA Concepts Covered:
1. Linear Search (Sequential search across unordered lists)
   - Best Case: O(1) - target is at the first index
   - Average Case: O(n) - target is in the middle
   - Worst Case: O(n) - target is at the end or not present
   - Space Complexity: O(1) - auxiliary space is constant

2. Binary Search (Divide-and-Conquer on sorted arrays)
   - Best Case: O(1) - middle element matches target
   - Average Case: O(log n) - search space halved each iteration
   - Worst Case: O(log n)
   - Space Complexity: O(1) - iterative implementation avoids call stack overhead
=============================================================================
"""

from typing import List, Any, Optional, Callable


def linear_search(
    items: List[Any],
    predicate: Callable[[Any], bool]
) -> List[Any]:
    """
    Performs Linear Search across a list of items using a matching predicate.
    
    Why used:
        For flexible multi-field filtering (e.g., checking if search term appears
        in movie title, genre, language, or theatre name) where data is not
        strictly sorted by that criterion.
        
    Complexity:
        Time: O(n) where n is number of items
        Space: O(k) where k is the number of matching items found
    """
    matches = []
    for item in items:
        if predicate(item):
            matches.append(item)
    return matches


def binary_search(
    items: List[Any],
    target_value: Any,
    key_func: Callable[[Any], Any]
) -> Optional[Any]:
    """
    Performs Iterative Binary Search on a list sorted in ascending order.
    
    Parameters:
        items: List of sorted items (e.g., movies sorted by id or title).
        target_value: The value we are seeking.
        key_func: Function to extract comparison key from each item.
        
    Returns:
        The matching item, or None if target_value is not found.
        
    Complexity:
        Time: O(log n)
        Space: O(1)
    """
    low = 0
    high = len(items) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = key_func(items[mid])

        if mid_val == target_value:
            return items[mid]
        elif mid_val < target_value:
            low = mid + 1
        else:
            high = mid - 1

    return None


def binary_search_range(
    items: List[Any],
    min_val: Any,
    max_val: Any,
    key_func: Callable[[Any], Any]
) -> List[Any]:
    """
    Finds all items within [min_val, max_val] in an array sorted ascendingly.
    Uses binary search to locate boundary indices in O(log n), then slices.
    
    Complexity:
        Time: O(log n + k) where k is the number of elements in range
        Space: O(k)
    """
    if not items:
        return []

    # 1. Binary search for left boundary (first element >= min_val)
    low, high = 0, len(items) - 1
    left_idx = len(items)
    while low <= high:
        mid = (low + high) // 2
        if key_func(items[mid]) >= min_val:
            left_idx = mid
            high = mid - 1
        else:
            low = mid + 1

    # 2. Binary search for right boundary (last element <= max_val)
    low, high = 0, len(items) - 1
    right_idx = -1
    while low <= high:
        mid = (low + high) // 2
        if key_func(items[mid]) <= max_val:
            right_idx = mid
            low = mid + 1
        else:
            high = mid - 1

    if left_idx <= right_idx and 0 <= left_idx < len(items) and 0 <= right_idx < len(items):
        return items[left_idx:right_idx + 1]
    return []
