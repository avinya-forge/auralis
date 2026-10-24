"""
Auralis - Local LLM Classifier & Intelligent Metadata Extraction Engine
Integrates with locally running LLMs (Ollama, LM Studio, LocalAI) with
seamless fallback to deterministic rule engines when LLM is offline.
"""

import json
import logging
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("auralis.llm")

class LocalLLMClassifier:
    """
    Connects to local LLM instances (e.g., Ollama at localhost:11434, LM Studio at localhost:1234)
    to classify ambiguous song titles and identify language, movie, and clean track titles.
    """

    def __init__(
        self,
        endpoint_url: str = "http://localhost:11434/api/generate",
        model_name: str = "llama3:latest",
        timeout_seconds: float = 3.0
    ):
        self.endpoint_url = endpoint_url
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self._is_available: Optional[bool] = None

    def check_availability(self) -> bool:
        """Checks whether the local LLM service is running and responsive."""
        if self._is_available is not None:
            return self._is_available

        try:
            # Check Ollama tags or root endpoint
            base_url = self.endpoint_url.rsplit("/api/", 1)[0]
            req = urllib.request.Request(f"{base_url}/api/tags", headers={"User-Agent": "Auralis/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                if response.status == 200:
                    self._is_available = True
                    return True
        except Exception:
            pass

        self._is_available = False
        return False

    def classify_ambiguous_track(
        self,
        filename: str,
        artist: str = "",
        album: str = "",
        title: str = ""
    ) -> Optional[Dict[str, str]]:
        """
        Queries the local LLM to extract clean metadata from ambiguous track filenames.
        Returns a dict with 'language', 'movie_or_album', 'title', 'artist' or None on failure.
        """
        if not self.check_availability():
            return None

        prompt = (
            f"You are a music metadata expert. Identify the song from this filename and metadata:\n"
            f"Filename: {filename}\n"
            f"Tags - Artist: {artist}, Album: {album}, Title: {title}\n"
            f"Return ONLY valid JSON with keys: 'language', 'movie_or_album', 'title', 'artist'.\n"
            f"Language must be one of: Hindi, Marathi, English, Sanskrit, Pravachan."
        )

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint_url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "Auralis/1.0"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode("utf-8"))
                    response_text = result.get("response", "{}")
                    parsed = json.loads(response_text)
                    if "language" in parsed and "title" in parsed:
                        return {
                            "language": parsed.get("language", "Hindi"),
                            "movie_or_album": parsed.get("movie_or_album", "Bollywood Classics"),
                            "title": parsed.get("title", filename),
                            "artist": parsed.get("artist", "Various Artists")
                        }
        except Exception as e:
            logger.debug(f"Local LLM query failed for {filename}: {e}")

        return None
