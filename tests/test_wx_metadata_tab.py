"""
Unit tests for wxPython Metadata Tab
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx before importing module under test
if "wx" not in sys.modules:
    mock_wx = MagicMock()

    class MockPanel:
        def __init__(self, parent=None, *args, **kwargs):
            pass

        def SetSizer(self, sizer):
            pass

    class MockSizer:
        def __init__(self, *args, **kwargs):
            pass

        def Add(self, *args, **kwargs):
            pass

    def MockWidget(parent=None, *args, **kwargs):
        return MagicMock()

    # Mock base classes
    mock_wx.Panel = MockPanel
    mock_wx.BoxSizer = MockSizer
    mock_wx.StaticBox = MockWidget
    mock_wx.StaticBoxSizer = MockSizer
    mock_wx.StaticText = MockWidget
    mock_wx.Button = MockWidget
    mock_wx.CheckBox = MockWidget
    mock_wx.MessageBox = MagicMock()

    # Constants
    mock_wx.VERTICAL = 1
    mock_wx.HORIZONTAL = 2
    mock_wx.ALL = 4
    mock_wx.EXPAND = 8
    mock_wx.LEFT = 16
    mock_wx.BOTTOM = 32
    mock_wx.RIGHT = 64
    mock_wx.ALIGN_CENTER = 128
    mock_wx.ALIGN_RIGHT = 256
    mock_wx.ID_OK = 5100
    mock_wx.OK = 0
    mock_wx.ICON_INFORMATION = 0

    # Event binding
    mock_wx.EVT_BUTTON = MagicMock()

    # Ensure wx.lib exists
    mock_wx.lib = MagicMock()
    mock_wx.lib.newevent = MagicMock()

    # Mock NewEvent to return (EventClass, Binder)
    def mock_new_event():
        class Event:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        return Event, MagicMock()

    mock_wx.lib.newevent.NewEvent = mock_new_event

    sys.modules["wx.lib"] = mock_wx.lib
    sys.modules["wx.lib.newevent"] = mock_wx.lib.newevent

    sys.modules["wx"] = mock_wx

# Import module under test
from src.gui.wx.tabs.metadata_tab import MetadataTab


class TestMetadataTab(unittest.TestCase):

    def setUp(self):
        self.mock_parent = MagicMock()

        # Patch get_config
        self.config_patcher = patch("src.gui.wx.tabs.metadata_tab.get_config")
        self.mock_get_config = self.config_patcher.start()
        self.mock_get_config.return_value = True

    def tearDown(self):
        self.config_patcher.stop()

    def test_initialization(self):
        """Test tab initialization"""
        tab = MetadataTab(self.mock_parent)

        # Verify UI elements
        self.assertTrue(hasattr(tab, "mb_check"))
        self.assertTrue(hasattr(tab, "discogs_check"))
        self.assertTrue(hasattr(tab, "spotify_check"))
        self.assertTrue(hasattr(tab, "lastfm_check"))
        self.assertTrue(hasattr(tab, "lyrics_check"))

        # Verify config usage
        self.mock_get_config.assert_any_call("USE_MUSICBRAINZ", True)

    def test_get_options(self):
        """Test retrieving options"""
        tab = MetadataTab(self.mock_parent)

        tab.mb_check.GetValue.return_value = True
        tab.discogs_check.GetValue.return_value = False
        tab.spotify_check.GetValue.return_value = True
        tab.lastfm_check.GetValue.return_value = False
        tab.lyrics_check.GetValue.return_value = True

        options = tab.get_options()

        self.assertTrue(options["use_musicbrainz"])
        self.assertFalse(options["use_discogs"])
        self.assertTrue(options["use_spotify"])
        self.assertFalse(options["use_lastfm"])
        self.assertTrue(options["fetch_lyrics"])

    def test_configure_api_keys(self):
        """Test opening API keys dialog"""
        tab = MetadataTab(self.mock_parent)
        mock_event = MagicMock()

        # Mock APIKeysDialog
        mock_dlg = MagicMock()
        mock_dlg.ShowModal.return_value = sys.modules["wx"].ID_OK

        with patch("src.gui.wx.tabs.metadata_tab.APIKeysDialog", return_value=mock_dlg) as MockDlg:
            tab.on_configure_api_keys(mock_event)

            MockDlg.assert_called_with(tab)
            mock_dlg.ShowModal.assert_called_once()
            sys.modules["wx"].MessageBox.assert_called()
            mock_dlg.Destroy.assert_called_once()

    def test_update_clicked(self):
        """Test update button click"""
        tab = MetadataTab(self.mock_parent)
        mock_event = MagicMock()

        tab.on_update_clicked(mock_event)
        mock_event.Skip.assert_called_once()


if __name__ == "__main__":
    unittest.main()
