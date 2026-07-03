import json
import os
import tempfile
import unittest

from src.modules.db.cleanup import cleanup_orphaned_metadata
from src.utils.db_utils import get_db_connection


class TestDBCleanup(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.test_dir = tempfile.mkdtemp()

        with get_db_connection(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    file_hash TEXT PRIMARY KEY,
                    data TEXT,
                    last_updated REAL
                )
                """)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        import shutil

        shutil.rmtree(self.test_dir)

    def test_cleanup_orphaned_metadata_deletes_rows(self):
        # Create a valid file
        valid_file = os.path.join(self.test_dir, "exists.mp3")
        with open(valid_file, "w") as f:
            f.write("test")

        missing_file = os.path.join(self.test_dir, "missing.mp3")

        data_valid = json.dumps({"path": valid_file, "title": "Valid"})
        data_missing = json.dumps({"file_path": missing_file, "title": "Missing"})

        with get_db_connection(self.db_path) as conn:
            conn.execute(
                "INSERT INTO metadata (file_hash, data) VALUES (?, ?)", ("hash1", data_valid)
            )
            conn.execute(
                "INSERT INTO metadata (file_hash, data) VALUES (?, ?)", ("hash2", data_missing)
            )

        deleted = cleanup_orphaned_metadata(self.db_path)

        self.assertEqual(deleted, 1)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.execute("SELECT file_hash FROM metadata")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "hash1")


if __name__ == "__main__":
    unittest.main()
