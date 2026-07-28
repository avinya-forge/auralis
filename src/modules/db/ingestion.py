"""
Auralis - Database Ingestion Module
Handles user audio uploads and staging.
"""

import hashlib
import os
from time import strftime
from typing import Any, Dict, Optional


class ChunkedUploadHandler:
    """
    Handles chunked file uploads and verifies integrity via hashing.
    """

    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def write_chunk(self, file_id: str, chunk_index: int, data: bytes) -> str:
        """
        Writes a chunk to a temporary file.
        Returns the path to the chunk file.
        """
        chunk_path = os.path.join(self.upload_dir, f"{file_id}.part{chunk_index}")
        with open(chunk_path, "wb") as f:
            f.write(data)
        return chunk_path

    def assemble_file(self, file_id: str, total_chunks: int, expected_hash: str) -> Optional[str]:
        """
        Assembles all chunks into a final file and verifies the hash.
        Returns the path to the final file if successful, else None.
        """
        final_path = os.path.join(self.upload_dir, f"{file_id}.audio")
        sha256 = hashlib.sha256()

        try:
            with open(final_path, "wb") as outfile:
                for i in range(total_chunks):
                    chunk_path = os.path.join(self.upload_dir, f"{file_id}.part{i}")
                    if not os.path.exists(chunk_path):
                        return None

                    with open(chunk_path, "rb") as infile:
                        data = infile.read()
                        sha256.update(data)
                        outfile.write(data)

                    os.remove(chunk_path)

            if sha256.hexdigest() == expected_hash:
                return final_path

            if os.path.exists(final_path):
                os.remove(final_path)
            return None
        except Exception as e:
            _ = e
            if os.path.exists(final_path):
                os.remove(final_path)
            return None


class StagingMetadataExtractor:
    """
    Extracts metadata from staged audio files and prepares them for validation.
    """

    def __init__(self, metadata_service: Any):
        self.metadata_service = metadata_service

    def extract_and_stage(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """
        Extracts tags and returns a staging-ready dictionary.
        """
        if not os.path.exists(file_path):
            return {"file_id": file_id, "error": "File not found"}

        try:
            # We assume metadata_service.extract_metadata returns a dict
            raw_metadata = self.metadata_service.extract_metadata(file_path)

            # Prepare staging record
            staged_record = {
                "file_id": file_id,
                "path": file_path,
                "raw_tags": raw_metadata,
                "status": "pending_validation",
                "extracted_at": strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            return staged_record
        except Exception as e:
            return {"file_id": file_id, "error": str(e), "status": "extraction_failed"}
