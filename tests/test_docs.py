"""
Tests for documentation existence and sanity
"""

from pathlib import Path


class TestDocumentation:
    def test_backlog_exists(self):
        """Ensure backlog.md exists and is not empty"""
        path = Path("docs/backlog.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_release_notes_exists(self):
        """Ensure release-notes.md exists and is not empty"""
        path = Path("docs/release-notes.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_vision_exists(self):
        """Ensure vision.md exists and is not empty"""
        path = Path("docs/vision.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_standards_exists(self):
        """Ensure ultra-lean.md exists and is not empty"""
        path = Path("docs/standards/ultra-lean.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_user_guide_exists(self):
        """Ensure user guide is now within vision.md"""
        path = Path("docs/vision.md")
        content = path.read_text(encoding="utf-8")
        assert "## User Guide" in content

    def test_user_guide_content(self):
        """Check user guide (inside vision.md) for essential sections"""
        path = Path("docs/vision.md")
        content = path.read_text(encoding="utf-8")
        assert "### Installation" in content
        assert "### Troubleshooting" in content
