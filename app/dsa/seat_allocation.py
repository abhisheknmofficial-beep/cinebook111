"""
=============================================================================
CineBook DSA Module: 2D Seat Matrix & Allocation Algorithm
=============================================================================
Models the auditorium seating layout as a 2D Matrix (Grid) and implements
intelligent contiguous seat allocation and validation algorithms.

DSA Concepts Covered:
1. 2D Matrix / Grid Representation:
   - Rows indexed 0..R-1 (labels 'A', 'B', 'C'...)
   - Columns indexed 0..C-1 (numbers 1, 2, 3...)
   - Direct coordinate access grid[r][c] in O(1) time.
   - Space Complexity: O(R * C)

2. Contiguous Seat Allocation (Sliding Window Algorithm):
   - When a user requests k contiguous seats for friends/family,
     scans rows from optimal center outward using a sliding window.
   - Time Complexity: O(R * C) where R is total rows and C is columns.
   - Space Complexity: O(k) to return contiguous candidate coordinates.

3. Atomic Collision Validation:
   - Validates that none of the candidate seat IDs overlap with already booked seats.
   - Uses Hash Set for O(1) membership check -> total O(k) validation time.
=============================================================================
"""

from typing import List, Dict, Optional, Tuple, Set


class SeatNode:
    """Represents a discrete seat cell inside the auditorium matrix."""
    def __init__(
        self,
        seat_id: int,
        row_label: str,
        col_number: int,
        seat_code: str,
        seat_type: str = "REGULAR",
        base_price: float = 200.0,
        is_booked: bool = False
    ):
        self.seat_id = seat_id
        self.row_label = row_label
        self.col_number = col_number
        self.seat_code = seat_code
        self.seat_type = seat_type.upper()
        self.base_price = base_price
        self.is_booked = is_booked

    @property
    def price(self) -> float:
        """Computes pricing based on seating tier multiplier."""
        multiplier = 1.0
        if self.seat_type == "PREMIUM":
            multiplier = 1.25
        elif self.seat_type == "VIP":
            multiplier = 1.50
        return round(self.base_price * multiplier, 2)

    def to_dict(self) -> Dict:
        return {
            "seat_id": self.seat_id,
            "row": self.row_label,
            "col": self.col_number,
            "code": self.seat_code,
            "type": self.seat_type,
            "price": self.price,
            "status": "BOOKED" if self.is_booked else "AVAILABLE"
        }


class SeatGridMatrix:
    """
    2D Auditorium Seating Matrix manager.
    """
    def __init__(self, rows: int = 5, cols: int = 8, base_price: float = 200.0):
        self.num_rows = rows
        self.num_cols = cols
        self.base_price = base_price
        # 2D Array: rows x cols
        self.grid: List[List[Optional[SeatNode]]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]
        self._seat_id_map: Dict[int, Tuple[int, int]] = {}
        self._seat_code_map: Dict[str, Tuple[int, int]] = {}

    def populate_seats(self, seats_data: List[Any], booked_seat_ids: Set[int]) -> None:
        """
        Builds the 2D matrix from database seat records and marks booked seats.
        Time Complexity: O(N) where N is total seats.
        """
        for s in seats_data:
            row_idx = ord(s.row_label.upper()) - ord('A')
            col_idx = s.seat_number - 1

            if 0 <= row_idx < self.num_rows and 0 <= col_idx < self.num_cols:
                is_booked = s.id in booked_seat_ids
                node = SeatNode(
                    seat_id=s.id,
                    row_label=s.row_label.upper(),
                    col_number=s.seat_number,
                    seat_code=s.seat_code,
                    seat_type=getattr(s, "seat_type", "REGULAR"),
                    base_price=self.base_price,
                    is_booked=is_booked
                )
                self.grid[row_idx][col_idx] = node
                self._seat_id_map[s.id] = (row_idx, col_idx)
                self._seat_code_map[s.seat_code] = (row_idx, col_idx)

    def get_seat(self, row_idx: int, col_idx: int) -> Optional[SeatNode]:
        if 0 <= row_idx < self.num_rows and 0 <= col_idx < self.num_cols:
            return self.grid[row_idx][col_idx]
        return None

    def get_seat_by_id(self, seat_id: int) -> Optional[SeatNode]:
        coords = self._seat_id_map.get(seat_id)
        if coords:
            return self.grid[coords[0]][coords[1]]
        return None

    def validate_seats_available(self, requested_seat_ids: List[int]) -> Tuple[bool, str, List[SeatNode]]:
        """
        Validates whether all requested seat IDs are present and currently AVAILABLE.
        Prevents double-booking.
        
        Returns:
            (is_valid: bool, error_message: str, validated_nodes: List[SeatNode])
        """
        if not requested_seat_ids:
            return False, "No seats selected for booking.", []

        # Check for duplicates within the requested list itself
        if len(requested_seat_ids) != len(set(requested_seat_ids)):
            return False, "Duplicate seat IDs in selection request.", []

        selected_nodes: List[SeatNode] = []
        for sid in requested_seat_ids:
            seat_node = self.get_seat_by_id(sid)
            if not seat_node:
                return False, f"Seat ID {sid} does not exist in this auditorium.", []
            if seat_node.is_booked:
                return False, f"Seat {seat_node.seat_code} is already booked by another user.", []
            selected_nodes.append(seat_node)

        return True, "", selected_nodes

    def find_contiguous_seats(self, count: int) -> List[SeatNode]:
        """
        Sliding Window Algorithm to recommend 'count' contiguous available seats.
        Evaluates middle rows first for optimal cinematic viewing angles.
        
        Time Complexity: O(R * C)
        Space Complexity: O(k)
        """
        if count <= 0 or count > self.num_cols:
            return []

        # Row priority: start from center row and alternate outwards
        center_row = self.num_rows // 2
        row_order = [center_row]
        for offset in range(1, self.num_rows):
            if center_row - offset >= 0:
                row_order.append(center_row - offset)
            if center_row + offset < self.num_rows:
                row_order.append(center_row + offset)

        for r in row_order:
            row_seats = self.grid[r]
            # Sliding window of width 'count'
            for start_col in range(0, self.num_cols - count + 1):
                window = row_seats[start_col:start_col + count]
                # Check if all seats in window are present and unbooked
                if all(seat is not None and not seat.is_booked for seat in window):
                    return [seat for seat in window if seat is not None]

        return []

    def to_matrix_json(self) -> List[List[Dict]]:
        """Returns 2D JSON representation for frontend visual seat map."""
        matrix = []
        for r in range(self.num_rows):
            row_list = []
            for c in range(self.num_cols):
                seat = self.grid[r][c]
                if seat:
                    row_list.append(seat.to_dict())
                else:
                    row_list.append(None)
            matrix.append(row_list)
        return matrix
