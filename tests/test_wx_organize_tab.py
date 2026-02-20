"""
Unit tests for wxPython Organize Tab
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx before importing module under test
if "wx" not in sys.modules:
    mock_wx = MagicMock()

    # Define a proper base class for Panel to avoid InvalidSpecError
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
    mock_wx.DirDialog = MockWidget
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
    mock_wx.DD_DEFAULT_STYLE = 0
    mock_wx.ICON_WARNING = 0
    mock_wx.ICON_INFORMATION = 0
    mock_wx.OK = 0

    # Event binding
    mock_wx.EVT_BUTTON = MagicMock()
    mock_wx.EVT_CHECKBOX = MagicMock()

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
from src.gui.wx.tabs.organize_tab import OrganizeTab


class TestOrganizeTab(unittest.TestCase):

    def setUp(self):
        self.mock_parent = MagicMock()

        # Patch get_config
        self.config_patcher = patch("src.gui.wx.tabs.organize_tab.get_config")
        self.mock_get_config = self.config_patcher.start()
        # Set default config values
        self.mock_get_config.return_value = True

    def tearDown(self):
        self.config_patcher.stop()

    def test_initialization(self):
        """Test tab initialization"""
        tab = OrganizeTab(self.mock_parent)

        # Verify UI elements created
        self.assertTrue(hasattr(tab, "dest_label"))
        self.assertTrue(hasattr(tab, "lang_org_check"))
        self.assertTrue(hasattr(tab, "audio_similarity_check"))

        # Verify config was used
        self.mock_get_config.assert_any_call("ORGANIZE_BY_LANGUAGE", True)

    def test_default_output_dir(self):
        """Test initialization with default output dir"""
        with patch("os.path.exists", return_value=True):
            tab = OrganizeTab(self.mock_parent, default_output_dir="/tmp/test")
            # Verify SetLabel was called on the mock created by wx.StaticText
            # Since wx.StaticText() returns a new mock, and tab.dest_label holds it
            tab.dest_label.SetLabel.assert_called_with("/tmp/test")

    def test_get_options(self):
        """Test retrieving options from UI"""
        tab = OrganizeTab(self.mock_parent)

        # Mock values
        tab.lang_org_check.GetValue.return_value = True
        tab.audio_lang_detect_check.GetValue.return_value = False
        tab.audio_similarity_check.GetValue.return_value = True
        tab.keep_duplicates_check.GetValue.return_value = False
        tab.dup_check.GetValue.return_value = True
        tab.empty_dirs_check.GetValue.return_value = True

        options = tab.get_options()

        self.assertTrue(options["organize_by_language"])
        self.assertFalse(options["use_audio_language_detection"])
        self.assertTrue(options["detect_audio_similarity"])
        self.assertFalse(options["keep_all_duplicates"])
        self.assertTrue(options["handle_duplicates"])
        self.assertTrue(options["remove_empty_dirs"])

    def test_toggles(self):
        """Test checkbox toggle logic"""
        tab = OrganizeTab(self.mock_parent)

        # Language toggle
        mock_event = MagicMock()

        # Enable
        tab.lang_org_check.GetValue.return_value = True
        tab.on_lang_org_toggled(mock_event)
        tab.audio_lang_detect_check.Enable.assert_called_with(True)

        # Disable
        tab.lang_org_check.GetValue.return_value = False
        tab.on_lang_org_toggled(mock_event)
        tab.audio_lang_detect_check.Enable.assert_called_with(False)

        # Similarity toggle
        tab.audio_similarity_check.GetValue.return_value = True
        tab.on_similarity_toggled(mock_event)
        tab.keep_duplicates_check.Enable.assert_called_with(True)

    def test_destination_selection(self):
        """Test destination directory selection"""
        tab = OrganizeTab(self.mock_parent)

        # Mock DirDialog
        mock_dlg = MagicMock()
        mock_dlg.ShowModal.return_value = sys.modules["wx"].ID_OK
        mock_dlg.GetPath.return_value = "/new/path"

        with patch("src.gui.wx.tabs.organize_tab.wx.DirDialog", return_value=mock_dlg):
            tab.on_select_destination(MagicMock())

            tab.dest_label.SetLabel.assert_called_with("/new/path")
            mock_dlg.Destroy.assert_called_once()

    def test_validation(self):
        """Test validation logic"""
        tab = OrganizeTab(self.mock_parent)

        # Invalid
        tab.dest_label.GetLabel.return_value = "No destination selected"
        self.assertFalse(tab.validate_destination())
        sys.modules["wx"].MessageBox.assert_called()

        # Valid
        tab.dest_label.GetLabel.return_value = "/valid/path"
        self.assertTrue(tab.validate_destination())

    def test_organize_clicked(self):
        """Test organize button click"""
        tab = OrganizeTab(self.mock_parent)
        mock_event = MagicMock()

        # Invalid destination
        tab.dest_label.GetLabel.return_value = "No destination selected"
        tab.on_organize_clicked(mock_event)
        mock_event.Skip.assert_not_called()

        # Valid destination
        tab.dest_label.GetLabel.return_value = "/valid/path"
        tab.on_organize_clicked(mock_event)
        mock_event.Skip.assert_called_once()

    def test_dry_run_clicked(self):
        """Test dry run button click"""
        tab = OrganizeTab(self.mock_parent)
        mock_event = MagicMock()

        # Valid destination
        tab.dest_label.GetLabel.return_value = "/valid/path"
        tab.on_dry_run_clicked(mock_event)
        mock_event.Skip.assert_called_once()


if __name__ == "__main__":
    unittest.main()
