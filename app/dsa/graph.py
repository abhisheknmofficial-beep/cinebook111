"""
=============================================================================
CineBook DSA Module: Graph Relationship & Traversal
=============================================================================
Models the entertainment ecosystem as a multi-tier directed Graph:
  Movie ──> Theatre ──> Screen ──> Show ──> Seats

DSA Concepts Covered:
1. Graph Representation (Adjacency List):
   - Vertices (V): Movies, Theatres, Screens, Shows, Seats
   - Edges (E): Directed relationships ("ScreenedAt", "ContainsScreen", "SchedulesShow", "ProvidesSeat")
   - Space Complexity: O(V + E)

2. Breadth-First Search (BFS):
   - Explores neighbors layer-by-layer using a FIFO queue.
   - Used to discover all theatres and shows running a movie across cities.
   - Time Complexity: O(V + E)
   - Space Complexity: O(V)

3. Depth-First Search (DFS):
   - Explores deep paths recursively to validate full reservation lineage
     (Movie -> Theatre -> Screen -> Show -> Seat).
   - Time Complexity: O(V + E)
   - Space Complexity: O(V)
=============================================================================
"""

from typing import Dict, List, Set, Optional, Any
from collections import deque


class GraphNode:
    """Represents an entity node inside the CineBook booking graph."""
    def __init__(self, node_id: str, node_type: str, data: Optional[Dict] = None):
        self.node_id = node_id          # e.g., "movie:1", "theatre:2", "show:5"
        self.node_type = node_type      # "MOVIE", "THEATRE", "SCREEN", "SHOW", "SEAT"
        self.data = data or {}

    def __repr__(self):
        return f"<GraphNode {self.node_id} ({self.node_type})>"


class BookingGraph:
    """
    Adjacency List Graph representing the hierarchical relationships
    in movie and show scheduling.
    """
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.adjacency: Dict[str, List[str]] = {}

    def add_node(self, node_id: str, node_type: str, data: Optional[Dict] = None) -> GraphNode:
        if node_id not in self.nodes:
            node = GraphNode(node_id, node_type, data)
            self.nodes[node_id] = node
            self.adjacency[node_id] = []
        return self.nodes[node_id]

    def add_edge(self, from_id: str, to_id: str) -> None:
        """Adds a directed relationship from parent node to child node."""
        if from_id in self.nodes and to_id in self.nodes:
            if to_id not in self.adjacency[from_id]:
                self.adjacency[from_id].append(to_id)

    def bfs_find_shows_for_movie(self, movie_id: int, city_filter: Optional[str] = None) -> List[Dict]:
        """
        Uses BFS to traverse Movie -> Theatre -> Screen -> Show.
        Filters shows optionally by theatre city.
        
        Complexity: O(V + E)
        """
        start_id = f"movie:{movie_id}"
        if start_id not in self.nodes:
            return []

        results = []
        queue = deque([start_id])
        visited: Set[str] = {start_id}

        while queue:
            curr_id = queue.popleft()
            curr_node = self.nodes[curr_id]

            if curr_node.node_type == "SHOW":
                results.append(curr_node.data)

            for neighbor_id in self.adjacency.get(curr_id, []):
                neighbor = self.nodes.get(neighbor_id)
                if neighbor and neighbor_id not in visited:
                    # Optional city filtering at theatre layer
                    if neighbor.node_type == "THEATRE" and city_filter:
                        theatre_city = (neighbor.data.get("city") or "").lower()
                        if theatre_city != city_filter.lower():
                            continue
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

        return results

    def dfs_trace_lineage(self, start_id: str, path: Optional[List[str]] = None) -> List[List[str]]:
        """
        Uses DFS to discover all full lineage paths starting from a given node.
        Example: ["movie:1", "theatre:2", "screen:3", "show:4", "seat:5"]
        
        Complexity: O(V + E)
        """
        if path is None:
            path = [start_id]

        children = self.adjacency.get(start_id, [])
        if not children:
            return [path]

        all_paths = []
        for child_id in children:
            if child_id not in path:  # avoid cycles
                deeper_paths = self.dfs_trace_lineage(child_id, path + [child_id])
                all_paths.extend(deeper_paths)

        return all_paths
