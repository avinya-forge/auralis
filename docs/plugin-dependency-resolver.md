# Plugin Dependency Resolver Design

This document describes the architectural implementation of the `DependencyResolver` module responsible for validating and resolving complex third-party plugin hierarchies within Auralis.

## Objective

The `DependencyResolver` enforces robust startup mechanics. By validating plugin dependencies based on `metadata.json` definitions, it computes an execution order, preventing initialization if a circular dependency loop is detected.

## Implementation Details

### Kahn's Algorithm

The resolver applies topological sort logic (Kahn's algorithm) to compute a valid initialization sequence. Given an input dictionary representing a directed graph (where nodes are plugin IDs and edges define dependency relationships), the algorithm incrementally maps nodes with an in-degree of 0.

### Circular Dependency Detection

If Kahn's algorithm fails to output an initialization sequence whose length equals the total number of plugin nodes, a circular dependency exists. The module will automatically refuse to initialize the offending plugin subgraph.

### Example Architecture

```python
from typing import Dict, List, Set

class DependencyResolver:
    def __init__(self, plugin_manifests: List[dict]):
        self.manifests = {p['id']: p for p in plugin_manifests}
        self.dependencies = {p['id']: p.get('dependencies', []) for p in plugin_manifests}

    def resolve(self) -> List[str]:
        # Compute in-degrees
        in_degree = {u: 0 for u in self.dependencies}
        for u in self.dependencies:
            for v in self.dependencies[u]:
                in_degree[v] = in_degree.get(v, 0) + 1

        # Kahn's logic
        queue = [u for u in self.dependencies if in_degree[u] == 0]
        sorted_plugins = []

        while queue:
            u = queue.pop(0)
            sorted_plugins.append(u)
            for v in self.dependencies[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(sorted_plugins) != len(self.dependencies):
            raise CircularDependencyError("Detected circular dependency in plugin graph.")

        return sorted_plugins
```
