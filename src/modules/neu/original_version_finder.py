import logging
from datetime import datetime
from typing import Optional

import musicbrainzngs
import numpy as np

from src.modules.neu.embedding_database import EmbeddingDatabase

logger = logging.getLogger(__name__)


class OriginalVersionFinder:
    """
    Logic for finding the original version of a track based on audio similarity and release dates.
    """

    def __init__(self, embedding_db: EmbeddingDatabase):
        """
        Initialize the finder with an embedding database.

        Args:
            embedding_db: The EmbeddingDatabase instance to query.
        """
        self.embedding_db = embedding_db
        # Ensure useragent is set for MusicBrainz (usually set by metadata_service, but good to ensure here)
        try:
            musicbrainzngs.set_useragent(
                "Auralis_OriginalFinder", "0.1", "https://github.com/patternseekers/auralis"
            )
        except Exception as e:
            _ = e
            pass  # Ignore if already set

    def find_original(
        self, target_embedding: np.ndarray, model_version: Optional[str] = None
    ) -> Optional[str]:
        """
        Query the database for highly similar vectors, then fetch release dates
        from MusicBrainz to determine the original (oldest) track.

        Args:
            target_embedding: The numpy array of the target track's embedding.
            model_version: Optional model version to filter embeddings by.

        Returns:
            The track_id of the oldest track among the highly similar ones,
            or None if no original version could be found.
        """
        # Find similar tracks with > 0.9 similarity. We get top 50 to cast a wide net.
        similar_tracks = self.embedding_db.search_similar(
            target_embedding, top_k=50, model_version=model_version
        )

        candidates = []
        for track_id, similarity in similar_tracks:
            if similarity > 0.9:
                candidates.append(track_id)

        if not candidates:
            logger.info("No candidates with >0.9 similarity found.")
            return None

        oldest_track_id = None
        oldest_date: Optional[datetime] = None

        for track_id in candidates:
            # We assume track_id is a recording ID or search query for musicbrainz.
            # For simplicity, we search for the track_id as a query if it doesn't look like an MBID,
            # or use it directly. We'll try search first because track_id is a generic VARCHAR in DB.
            release_date = self._get_oldest_release_date(track_id)

            if release_date:
                if oldest_date is None or release_date < oldest_date:
                    oldest_date = release_date
                    oldest_track_id = track_id

        # If we couldn't find release dates for any, fallback to the most similar track
        # or just return the first one. Let's return the highest similarity track that has a date,
        # or if none have dates, return None.
        return oldest_track_id

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse MusicBrainz date string to datetime object."""
        try:
            if len(date_str) == 4:
                return datetime.strptime(date_str, "%Y")
            elif len(date_str) == 7:
                return datetime.strptime(date_str, "%Y-%m")
            else:
                return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            return None

    def _get_oldest_release_date(self, track_id: str) -> Optional[datetime]:
        """
        Helper to fetch the oldest release date for a given track identifier from MusicBrainz.
        """
        try:
            # We assume track_id could be a title or a file name without extension.
            # Using musicbrainzngs.search_recordings
            query = f'recording:"{track_id}"'
            results = musicbrainzngs.search_recordings(query=query, limit=5)

            if not results or "recording-list" not in results:
                return None

            recordings = results["recording-list"]
            oldest_date: Optional[datetime] = None

            for recording in recordings:
                if "release-list" in recording:
                    for release in recording["release-list"]:
                        if "date" in release:
                            parsed_date = self._parse_date(release["date"])
                            if parsed_date:
                                if oldest_date is None or parsed_date < oldest_date:
                                    oldest_date = parsed_date

            return oldest_date

        except Exception as e:
            logger.error(f"Error querying MusicBrainz for {track_id}: {e}")
            return None
