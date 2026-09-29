"""
=============================================================================
CineBook DSA Module: Hashing & Hash Table
=============================================================================
Provides both a custom educational Hash Table with separate chaining
and specialized caching layers using hash mappings for high-performance
lookups across the CineBook application.

DSA Concepts Covered:
1. Hash Table with Separate Chaining (Collision Resolution):
   - Computes hash index using bucket mod arithmetic: index = hash(key) % capacity
   - Collisions are resolved using bucket chaining (list of key-value pairs).
   - Dynamic Resizing / Re-hashing when load factor (n / capacity) exceeds threshold (0.75).
   - Time Complexity:
       Lookup:  Average O(1), Worst O(n) (when all keys hash to the same bucket)
       Insert:  Average O(1), Worst O(n)
       Delete:  Average O(1), Worst O(n)
   - Space Complexity: O(n + capacity)

2. Domain Hash Maps:
   - MovieFastIndex: O(1) key-value lookup by movie_id or title
   - SeatStatusMap: O(1) composite tuple lookup ((show_id, seat_id) -> status)
=============================================================================
"""

from typing import Any, List, Optional, Tuple, Dict


class HashNode:
    """Represents an entry node in a separate chaining bucket."""
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.next: Optional['HashNode'] = None


class ChainingHashTable:
    """
    Custom educational Hash Table implementing separate chaining
    for college DSA viva demonstration.
    """
    def __init__(self, initial_capacity: int = 16, load_factor_threshold: float = 0.75):
        self.capacity = initial_capacity
        self.size = 0
        self.load_factor_threshold = load_factor_threshold
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity

    def _hash(self, key: Any) -> int:
        """Computes hash index within current capacity."""
        if isinstance(key, int):
            raw_hash = key
        elif isinstance(key, str):
            # DJB2 hash algorithm
            h = 5381
            for char in key:
                h = ((h << 5) + h) + ord(char)
            raw_hash = h
        else:
            raw_hash = hash(key)
        return abs(raw_hash) % self.capacity

    def put(self, key: Any, value: Any) -> None:
        """Inserts or updates a key-value pair in O(1) average time."""
        index = self._hash(key)
        node = self.buckets[index]

        # Check if key already exists in the chain to update it
        current = node
        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next

        # Insert new node at head of chain
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1

        # Check if re-hashing is needed
        if (self.size / self.capacity) > self.load_factor_threshold:
            self._resize(self.capacity * 2)

    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieves value by key in O(1) average time."""
        index = self._hash(key)
        current = self.buckets[index]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return default

    def contains(self, key: Any) -> bool:
        """Checks existence of key in O(1) average time."""
        return self.get(key) is not None

    def delete(self, key: Any) -> bool:
        """Deletes key-value pair. Returns True if found and deleted."""
        index = self._hash(key)
        current = self.buckets[index]
        prev: Optional[HashNode] = None

        while current is not None:
            if current.key == key:
                if prev is None:
                    self.buckets[index] = current.next
                else:
                    prev.next = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next
        return False

    def _resize(self, new_capacity: int) -> None:
        """Doubles capacity and re-hashes all existing keys in O(n)."""
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [None] * new_capacity
        self.size = 0

        for head in old_buckets:
            current = head
            while current is not None:
                self.put(current.key, current.value)
                current = current.next

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"<ChainingHashTable(size={self.size}, capacity={self.capacity}, load={self.size/self.capacity:.2f})>"


class SeatStatusMap:
    """
    High-performance O(1) composite hash map for Show Seat states.
    Key: (show_id: int, seat_id: int)
    Value: 'AVAILABLE' | 'BOOKED' | 'HELD'
    """
    def __init__(self):
        self._map: Dict[Tuple[int, int], str] = {}

    def set_seat_status(self, show_id: int, seat_id: int, status: str) -> None:
        self._map[(show_id, seat_id)] = status

    def get_seat_status(self, show_id: int, seat_id: int, default: str = "AVAILABLE") -> str:
        return self._map.get((show_id, seat_id), default)

    def is_booked(self, show_id: int, seat_id: int) -> bool:
        return self._map.get((show_id, seat_id)) == "BOOKED"

    def bulk_load_booked_seats(self, booked_pairs: List[Tuple[int, int]]) -> None:
        """Loads a batch of booked seats into the hash map in O(k) time."""
        for show_id, seat_id in booked_pairs:
            self._map[(show_id, seat_id)] = "BOOKED"

    def clear_for_show(self, show_id: int) -> None:
        keys_to_delete = [k for k in self._map if k[0] == show_id]
        for k in keys_to_delete:
            del self._map[k]


class MovieLookupCache:
    """
    O(1) Hash Map index for instant movie retrieval by ID or slug/title.
    """
    def __init__(self):
        self._id_index: Dict[int, Any] = {}
        self._title_index: Dict[str, Any] = {}

    def insert(self, movie: Any) -> None:
        self._id_index[movie.id] = movie
        self._title_index[movie.title.lower()] = movie

    def get_by_id(self, movie_id: int) -> Optional[Any]:
        return self._id_index.get(movie_id)

    def get_by_title(self, title: str) -> Optional[Any]:
        return self._title_index.get(title.lower())

    def clear(self) -> None:
        self._id_index.clear()
        self._title_index.clear()
