import hashlib
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from src.modules.db.ingestion import ChunkedUploadHandler, StagingMetadataExtractor


class TestDBIngestion(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.handler = ChunkedUploadHandler(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_chunked_upload_and_assembly(self):
        file_id = "test_file"
        chunks = [b"chunk1", b"chunk2", b"chunk3"]
        full_data = b"".join(chunks)
        expected_hash = hashlib.sha256(full_data).hexdigest()

        for i, data in enumerate(chunks):
            self.handler.write_chunk(file_id, i, data)

        final_path = self.handler.assemble_file(file_id, len(chunks), expected_hash)

        self.assertIsNotNone(final_path)
        self.assertTrue(os.path.exists(final_path))
        with open(final_path, "rb") as f:
            self.assertEqual(f.read(), full_data)

    def test_assembly_invalid_hash(self):
        file_id = "bad_file"
        self.handler.write_chunk(file_id, 0, b"data")
        final_path = self.handler.assemble_file(file_id, 1, "wrong_hash")
        self.assertIsNone(final_path)

    def test_metadata_extraction(self):
        mock_service = MagicMock()
        mock_service.extract_metadata.return_value = {"title": "Test Song", "artist": "Test Artist"}

        extractor = StagingMetadataExtractor(mock_service)

        # Create a dummy file
        dummy_file = os.path.join(self.test_dir, "test.mp3")
        with open(dummy_file, "w") as f:
            f.write("dummy")

        result = extractor.extract_and_stage(dummy_file, "file123")

        self.assertEqual(result["file_id"], "file123")
        self.assertEqual(result["raw_tags"]["title"], "Test Song")
        self.assertEqual(result["status"], "pending_validation")
        self.assertIn("extracted_at", result)

    def test_metadata_extraction_file_not_found(self):
        extractor = StagingMetadataExtractor(MagicMock())
        result = extractor.extract_and_stage("non_existent.mp3", "file123")
        self.assertEqual(result["error"], "File not found")


if __name__ == "__main__":
    unittest.main()
