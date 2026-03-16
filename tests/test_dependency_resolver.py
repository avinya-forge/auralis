import json

import pytest

from src.modules.plg.dependency_resolver import DependencyResolver


def test_parse_metadata_missing_dir(tmp_path):
    resolver = DependencyResolver(str(tmp_path / "non_existent"))
    assert resolver.parse_metadata() == {}


def test_parse_metadata_no_plugins(tmp_path):
    resolver = DependencyResolver(str(tmp_path))
    assert resolver.parse_metadata() == {}


def test_parse_metadata_valid(tmp_path):
    # Setup plugin A
    plugin_a_dir = tmp_path / "plugin_a"
    plugin_a_dir.mkdir()
    with open(plugin_a_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({"id": "A", "dependencies": ["B", "C"]}, f)

    # Setup plugin B
    plugin_b_dir = tmp_path / "plugin_b"
    plugin_b_dir.mkdir()
    with open(plugin_b_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump({"id": "B", "dependencies": []}, f)

    resolver = DependencyResolver(str(tmp_path))
    graph = resolver.parse_metadata()

    assert "A" in graph
    assert "B" in graph
    assert graph["A"] == ["B", "C"]
    assert graph["B"] == []


def test_parse_metadata_invalid_json(tmp_path):
    plugin_dir = tmp_path / "plugin_bad"
    plugin_dir.mkdir()
    with open(plugin_dir / "metadata.json", "w", encoding="utf-8") as f:
        f.write("{invalid json")

    resolver = DependencyResolver(str(tmp_path))
    graph = resolver.parse_metadata()
    assert graph == {}


def test_resolve_independent_plugins(tmp_path, monkeypatch):
    resolver = DependencyResolver(str(tmp_path))
    monkeypatch.setattr(resolver, "parse_metadata", lambda: {"A": [], "B": [], "C": []})

    order = resolver.resolve()
    assert set(order) == {"A", "B", "C"}
    assert len(order) == 3


def test_resolve_linear_dependencies(tmp_path, monkeypatch):
    resolver = DependencyResolver(str(tmp_path))
    # A -> B -> C (A depends on B, B depends on C)
    # Order should be C, B, A
    monkeypatch.setattr(resolver, "parse_metadata", lambda: {"A": ["B"], "B": ["C"], "C": []})

    order = resolver.resolve()
    assert order == ["C", "B", "A"]


def test_resolve_complex_dag(tmp_path, monkeypatch):
    resolver = DependencyResolver(str(tmp_path))
    # A -> B, C
    # B -> D
    # C -> D
    # D -> []
    # D must be first. Then B and C (any order). Then A.
    monkeypatch.setattr(
        resolver, "parse_metadata", lambda: {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    )

    order = resolver.resolve()
    assert order[0] == "D"
    assert set(order[1:3]) == {"B", "C"}
    assert order[3] == "A"


def test_resolve_circular_dependency(tmp_path, monkeypatch):
    resolver = DependencyResolver(str(tmp_path))
    # A -> B
    # B -> A
    monkeypatch.setattr(resolver, "parse_metadata", lambda: {"A": ["B"], "B": ["A"]})

    with pytest.raises(ValueError, match="Circular dependency detected preventing initialization."):
        resolver.resolve()


def test_resolve_missing_dependency_in_metadata(tmp_path, monkeypatch):
    resolver = DependencyResolver(str(tmp_path))
    # A depends on B, but B has no metadata
    monkeypatch.setattr(resolver, "parse_metadata", lambda: {"A": ["B"]})

    order = resolver.resolve()
    # B should be resolved first, then A
    assert order == ["B", "A"]
