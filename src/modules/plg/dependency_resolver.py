import json
import os
from collections import deque
from typing import Dict, List, Any


class DependencyResolver:
    """
    Resolves plugin dependencies using Kahn's algorithm for topological sorting.
    """

    def __init__(self, plugin_dir: str):
        """
        Initialize the resolver with the base directory containing plugins.
        """
        self.plugin_dir = plugin_dir

    def parse_metadata(self) -> Dict[str, List[str]]:
        """
        Read and parse metadata.json from all plugin subdirectories into a dependency graph dict.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are plugin IDs and values are lists
                                  of plugin IDs they depend on.
        """
        graph: Dict[str, List[str]] = {}

        if not os.path.exists(self.plugin_dir):
            return graph

        for item in os.listdir(self.plugin_dir):
            item_path = os.path.join(self.plugin_dir, item)
            if os.path.isdir(item_path):
                metadata_path = os.path.join(item_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            metadata: Dict[str, Any] = json.load(f)
                            plugin_id = metadata.get("id", item)
                            dependencies = metadata.get("dependencies", [])
                            graph[plugin_id] = dependencies
                    except (json.JSONDecodeError, OSError):
                        pass

        return graph

    def resolve(self) -> List[str]:
        """
        Resolve dependencies using Kahn's algorithm and return the execution order.

        Returns:
            List[str]: A list of plugin IDs in the order they should be initialized.

        Raises:
            ValueError: If a circular dependency is detected.
        """
        graph = self.parse_metadata()

        # Build in-degree map and adjacency list for Kahn's algorithm
        # We need plugins to be loaded *after* their dependencies.
        # So edges should go from dependency -> dependent.
        # graph[u] = [v, w] means u depends on v and w.
        # This means v and w must be loaded before u.
        # Edge direction: v -> u, w -> u

        in_degree: Dict[str, int] = {u: 0 for u in graph}
        adj_list: Dict[str, List[str]] = {u: [] for u in graph}

        self._build_graph(graph, in_degree, adj_list)

        # Kahn's Algorithm
        queue: deque[str] = deque([u for u in in_degree if in_degree[u] == 0])
        resolved_order: List[str] = []

        while queue:
            u = queue.popleft()
            resolved_order.append(u)

            for v in adj_list[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        # Circular dependency check
        if len(resolved_order) != len(in_degree):
            raise ValueError("Circular dependency detected preventing initialization.")

        return resolved_order

    def _build_graph(self, graph: Dict[str, List[str]], in_degree: Dict[str, int], adj_list: Dict[str, List[str]]) -> None:
        """
        Helper to build in-degree and adjacency list from the dependency graph.
        """
        # Ensure all dependencies exist in the graph
        for deps in graph.values():
            for v in deps:
                if v not in in_degree:
                    in_degree[v] = 0
                if v not in adj_list:
                    adj_list[v] = []

        # Populate based on v -> u edges
        for u, deps in graph.items():
            for v in deps:
                adj_list[v].append(u)
                in_degree[u] += 1
