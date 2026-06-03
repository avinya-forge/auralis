from typing import Any, Dict, List, Optional

import musicbrainzngs


class MetadataAggregator:
    """Aggregates metadata."""

    def __init__(self) -> None:
        self.sources: List[Dict[str, Any]] = []

    def aggregate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results."""
        agg: Dict[str, Any] = {}
        for res in results:
            for k, v in res.items():
                if k not in agg or not agg[k]:
                    agg[k] = v
        return agg

    def clear(self) -> None:
        """Clear."""
        self.sources = []


class MusicBrainzAggregator(MetadataAggregator):
    """MusicBrainz."""

    def search_recording(self, artist: str, title: str) -> List[Dict[str, Any]]:
        """Search."""
        try:
            res = musicbrainzngs.search_recordings(artist=artist, recording=title)
            return [
                {
                    "mbid": r.get("id"),
                    "title": r.get("title"),
                    "artist": r.get("artist-credit-phrase"),
                    "score": int(r.get("ext:score", 0)),
                }
                for r in res.get("recording-list", [])
            ]
        except Exception:
            return []

    def get_details(self, mbid: str) -> Dict[str, Any]:
        """Details."""
        try:
            r = musicbrainzngs.get_recording_by_id(mbid, includes=["releases"]).get("recording", {})
            return {
                "mbid": mbid,
                "title": r.get("title"),
                "artist": r.get("artist-credit-phrase"),
                "releases": [rel.get("title") for rel in r.get("release-list", [])],
            }
        except Exception:
            return {}


class SpotifyAggregator(MetadataAggregator):
    """Spotify."""

    def __init__(
        self, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ) -> None:
        super().__init__()
        self.client_id, self.client_secret, self.enabled = (
            client_id,
            client_secret,
            bool(client_id and client_secret),
        )

    def search_track(self, artist: str, title: str) -> List[Dict[str, Any]]:
        """Search."""
        return [{"source": "spotify", "title": title, "artist": artist}] if self.enabled else []
