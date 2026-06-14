from pathlib import Path
from typing import Generator

import pytest

from scripts.audit_db import audit_integrity
from src.utils.db_utils import get_db_connection


@pytest.fixture
def db_with_violations(tmp_path: Path) -> Generator[str, None, None]:
    db_path = str(tmp_path / "violations.db")
    with get_db_connection(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        # Create schema
        conn.executescript("""
            CREATE TABLE parent (id INTEGER PRIMARY KEY);
            CREATE TABLE child (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES parent(id)
            );
            """)
        # Insert violating row
        conn.execute("INSERT INTO child (id, parent_id) VALUES (1, 999);")
    yield db_path


@pytest.fixture
def db_without_violations(tmp_path: Path) -> Generator[str, None, None]:
    db_path = str(tmp_path / "clean.db")
    with get_db_connection(db_path) as conn:
        conn.executescript("""
            CREATE TABLE parent (id INTEGER PRIMARY KEY);
            CREATE TABLE child (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES parent(id)
            );
            INSERT INTO parent (id) VALUES (1);
            INSERT INTO child (id, parent_id) VALUES (1, 1);
            """)
    yield db_path


def test_audit_integrity_with_violations(db_with_violations: str) -> None:
    violations = audit_integrity(db_with_violations)
    assert len(violations) > 0
    # table, rowid, parent, fkid
    assert violations[0][0] == "child"
    assert violations[0][2] == "parent"


def test_audit_integrity_without_violations(db_without_violations: str) -> None:
    violations = audit_integrity(db_without_violations)
    assert len(violations) == 0
