"""
=============================================================================
CineBook DSA Module: Queue Data Structure
=============================================================================
Implements a FIFO (First-In, First-Out) Queue for booking transaction
simulation and waiting list order management.

DSA Concepts Covered:
1. FIFO Queue:
   - Elements are inserted at the rear (enqueue) and removed from front (dequeue).
   - Strict First-Come, First-Served (FCFS) order guarantee.
   - Time Complexity:
       Enqueue: O(1)
       Dequeue: O(1)
       Peek:    O(1)
       IsEmpty: O(1)
   - Space Complexity: O(n) where n is the number of queued elements.
   - Why used: In high-demand ticketing (such as blockbuster movie opening day),
     hundreds of users submit booking requests simultaneously.
     A FIFO Queue buffers requests and processes them sequentially, eliminating
     race conditions and preventing duplicate allocations.
=============================================================================
"""

from typing import Any, List, Optional
from datetime import datetime, timezone
from collections import deque


class QueueNode:
    """Node element for linked FIFO Queue implementation."""
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional['QueueNode'] = None


class FIFOQueue:
    """
    Linked FIFO Queue implementation built from scratch for DSA college viva.
    """
    def __init__(self, max_size: Optional[int] = None):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0
        self.max_size: Optional[int] = max_size

    def enqueue(self, item: Any) -> bool:
        """
        Adds an item to the back of the queue in O(1) time.
        Returns False if queue is at maximum capacity.
        """
        if self.max_size is not None and self._size >= self.max_size:
            return False

        new_node = QueueNode(item)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node

        self._size += 1
        return True

    def dequeue(self) -> Optional[Any]:
        """
        Removes and returns the front item from the queue in O(1) time.
        Returns None if queue is empty.
        """
        if self.is_empty():
            return None

        temp = self.front
        self.front = self.front.next

        if self.front is None:
            self.rear = None

        self._size -= 1
        return temp.data

    def peek(self) -> Optional[Any]:
        """Returns the item at the front without removing it in O(1) time."""
        if self.is_empty():
            return None
        return self.front.data

    def is_empty(self) -> bool:
        """Checks if the queue is empty in O(1) time."""
        return self.front is None

    def size(self) -> int:
        """Returns the number of elements in the queue in O(1) time."""
        return self._size

    def to_list(self) -> List[Any]:
        """Converts queue contents to a standard list for inspection."""
        items = []
        curr = self.front
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"<FIFOQueue(size={self._size}, front={self.peek()})>"


class BookingRequest:
    """Represents a discrete booking transaction payload in the queue."""
    def __init__(self, request_id: str, user_id: int, show_id: int, seat_ids: List[int]):
        self.request_id = request_id
        self.user_id = user_id
        self.show_id = show_id
        self.seat_ids = seat_ids
        self.created_at = datetime.now(timezone.utc)
        self.processed = False
        self.success = False
        self.message = ""

    def __repr__(self):
        return f"<BookingRequest {self.request_id} (User: {self.user_id}, Show: {self.show_id}, Seats: {self.seat_ids})>"


class BookingSimulationQueue:
    """
    Queue manager handling incoming concurrent booking requests in FCFS order.
    """
    def __init__(self):
        self._queue = FIFOQueue()
        self._processed_history: List[BookingRequest] = []

    def submit_request(self, request: BookingRequest) -> bool:
        """Enqueues a new booking request."""
        return self._queue.enqueue(request)

    def process_next(self) -> Optional[BookingRequest]:
        """Dequeues and marks next booking request for atomic execution."""
        req = self._queue.dequeue()
        if req:
            self._processed_history.append(req)
        return req

    def pending_count(self) -> int:
        return self._queue.size()

    def get_pending_requests(self) -> List[BookingRequest]:
        return self._queue.to_list()
