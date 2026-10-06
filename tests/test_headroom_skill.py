import ast
import os
import tempfile
from unittest.mock import MagicMock

from src.modules.agent.headroom_skill import CodeHeadroom


def test_strip_docstrings_and_names():
    headroom = CodeHeadroom(llm_bridge=MagicMock())
    source = '''
def my_func(a, b):
    """Docstring"""
    x = a + b
    return x
'''
    tree = ast.parse(source)
    func = tree.body[0]

    stripped = headroom._strip_docstrings_and_names(func)

    # Check that name is replaced
    assert stripped.name == "function"
    # Check that docstring is removed (only assignment and return left in body)
    assert len(stripped.body) == 2
    assert isinstance(stripped.body[0], ast.Assign)
    assert isinstance(stripped.body[1], ast.Return)


def test_analyze_file_duplicates():
    headroom = CodeHeadroom(llm_bridge=MagicMock())
    source = """
def func1(a):
    x = a * 2
    return x

def func2(b):
    y = b * 2
    return y
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
        f.write(source)
        filepath = f.name

    try:
        opportunities = headroom.analyze_file(filepath)
        assert len(opportunities) == 1
        assert opportunities[0]["type"] == "duplicate_logic"
        assert "Duplicate function logic detected" in opportunities[0]["description"]
    finally:
        os.remove(filepath)


def test_generate_refactoring_suggestions():
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = "Merge into a single utility function."

    headroom = CodeHeadroom(llm_bridge=mock_llm)

    opps = [{"description": "Dup logic", "file": "test.py", "type": "duplicate_logic"}]

    suggestions = headroom.generate_refactoring_suggestions(opps)

    assert len(suggestions) == 1
    assert suggestions[0]["suggestion"] == "Merge into a single utility function."
    mock_llm.generate_response.assert_called_once()


def test_inject_to_backlog():
    headroom = CodeHeadroom(llm_bridge=MagicMock())

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("# Backlog\n")
        backlog_path = f.name

    suggestions = [{"description": "Dup logic", "file": "test.py", "suggestion": "Do this."}]

    try:
        headroom.inject_to_backlog(suggestions, backlog_path=backlog_path)

        with open(backlog_path, "r") as f:
            content = f.read()

        assert "## 🛠️ Tech Debt" in content
        assert "Dup logic" in content
        assert "Do this" in content
    finally:
        os.remove(backlog_path)
