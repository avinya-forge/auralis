"""
Tests for documentation existence and sanity
"""

from pathlib import Path


class TestDocumentation:
    def test_backlog_exists(self):
        """Ensure backlog.md exists and is not empty"""
        path = Path("docs/management/backlog.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_release_notes_exists(self):
        """Ensure release-notes.md exists and is not empty"""
        path = Path("docs/management/release-notes.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_vision_exists(self):
        """Ensure vision.md exists and is not empty"""
        path = Path("docs/management/vision.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_standards_exists(self):
        """Ensure standards.md exists and is not empty"""
        path = Path("docs/guidelines/standards.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_user_guide_exists(self):
        """Ensure user_guide.md exists and is not empty"""
        path = Path("docs/guidelines/user_guide.md")
        assert path.exists()
        assert path.stat().st_size > 0

    def test_user_guide_content(self):
        """Check user guide for essential sections"""
        path = Path("docs/guidelines/user_guide.md")
        content = path.read_text(encoding="utf-8")
        assert "# Auralis User Guide" in content
        assert "## Installation" in content
        assert "## Troubleshooting" in content
