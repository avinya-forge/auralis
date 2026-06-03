"""
Auralis - Metadata Aggregators
External API integration for seeding the music knowledge graph.
"""

import logging
from typing import Any, Dict, List, Optional

import musicbrainzngs

logger = logging.getLogger(__name__)


class MusicBrainzAggregator:
    """
    Interfaces with MusicBrainz for high-fidelity metadata.
    """

    def __init__(self) -> None:
        musicbrainzngs.set_useragent("Auralis", "0.1", "https://github.com/patternseekers/auralis")

    def search_recording(self, artist: str, title: str) -> List[Dict[str, Any]]:
        """
        Search for a recording and return matching candidates.
        """
        try:
            result = musicbrainzngs.search_recordings(artist=artist, recording=title, limit=5)
            recordings = []
            for item in result.get("recording-list", []):
                recordings.append(
                    {
                        "mbid": item.get("id"),
                        "title": item.get("title"),
                        "artist": item.get("artist-credit-phrase"),
                        "score": int(item.get("ext:score", 0)),
                    }
                )
            return recordings
        except Exception as e:
            logger.error(f"MusicBrainz search failed: {e}")
            return []

    def get_details(self, mbid: str) -> Dict[str, Any]:
        """
        Get full details for a specific recording MBID.
        """
        try:
            result = musicbrainzngs.get_recording_by_id(mbid, includes=["artists", "releases"])
            rec = result.get("recording", {})
            return {
                "mbid": mbid,
                "title": rec.get("title"),
                "artist": rec.get("artist-credit-phrase"),
                "releases": [r.get("title") for r in rec.get("release-list", [])],
            }
        except Exception as e:
            logger.error(f"MusicBrainz lookup failed: {e}")
            return {}


class SpotifyAggregator:
    """
    Placeholder for Spotify integration.
    Marked as [BLOCKED] in backlog due to missing 'spotipy' dependency.
    """

    def __init__(
        self, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.enabled = client_id is not None and client_secret is not None

    def search_track(self, artist: str, title: str) -> List[Dict[str, Any]]:
        """
        Placeholder search.
        """
        if not self.enabled:
            return []
        # Implementation depends on spotipy
        return [{"source": "spotify", "note": "Integration blocked by missing dependencies"}]
