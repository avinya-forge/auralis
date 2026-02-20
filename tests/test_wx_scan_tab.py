import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx module
mock_wx = MagicMock()


class MockPanel:
    def __init__(self, parent=None, **kwargs):
        pass

    def SetSizer(self, sizer):
        pass

    def Bind(self, event, handler):
        pass


mock_wx.Panel = MockPanel


# Stateful mocks for controls
class MockCheckBox:
    def __init__(self, parent=None, label="", **kwargs):
        self.value = False

    def SetValue(self, val):
        self.value = val

    def GetValue(self):
        return self.value


class MockTextCtrl:
    def __init__(self, parent=None, value="", **kwargs):
        self.value = value

    def SetValue(self, val):
        self.value = val

    def GetValue(self):
        return self.value


class MockSpinCtrl:
    def __init__(self, parent=None, value="", min=0, max=100, initial=0, **kwargs):
        self.value = initial

    def SetValue(self, val):
        self.value = val

    def GetValue(self):
        return self.value


mock_wx.CheckBox = MockCheckBox
mock_wx.TextCtrl = MockTextCtrl
mock_wx.SpinCtrl = MockSpinCtrl

# Constants
mock_wx.VERTICAL = 1
mock_wx.HORIZONTAL = 2
mock_wx.EXPAND = 8
mock_wx.ALL = 16
mock_wx.RIGHT = 32
mock_wx.ALIGN_CENTER_VERTICAL = 512
mock_wx.ALIGN_CENTER = 1024
mock_wx.ID_OK = 5100
mock_wx.EVT_BUTTON = 10001
mock_wx.DD_DEFAULT_STYLE = 1
mock_wx.DD_DIR_MUST_EXIST = 2
mock_wx.NOT_FOUND = -1
mock_wx.ICON_WARNING = 100
mock_wx.OK = 4


class TestScanTab(unittest.TestCase):
    def setUp(self):
        # Patch sys.modules to inject our mock_wx
        self.modules_patcher = patch.dict(sys.modules, {"wx": mock_wx})
        self.modules_patcher.start()

        # Reload the module under test to ensure it binds to our mock_wx
        if "src.gui.wx.tabs.scan_tab" in sys.modules:
            del sys.modules["src.gui.wx.tabs.scan_tab"]

        import src.gui.wx.tabs.scan_tab

        self.module = src.gui.wx.tabs.scan_tab
        self.ScanTab = self.module.ScanTab

        # Reset mocks
        mock_wx.reset_mock()

        # Mock get_config
        self.config_patcher = patch("src.gui.wx.tabs.scan_tab.get_config")
        self.mock_get_config = self.config_patcher.start()

        # Default behavior for get_config
        def get_config_side_effect(key, default=None):
            if key == "RENAME_FILES":
                return True
            if key == "FILE_EXTENSIONS":
                return "mp3,flac"
            if key == "TEST_MODE_ENABLED":
                return True
            if key == "TEST_MODE_FILE_COUNT":
                return 10
            return default

        self.mock_get_config.side_effect = get_config_side_effect

    def tearDown(self):
        self.config_patcher.stop()
        self.modules_patcher.stop()

    def test_init(self):
        """Test initialization of UI components"""
        tab = self.ScanTab(None)
        self.assertTrue(hasattr(tab, "source_list"))
        self.assertTrue(hasattr(tab, "add_source_btn"))
        self.assertTrue(hasattr(tab, "remove_source_btn"))
        self.assertTrue(hasattr(tab, "extensions_edit"))
        self.assertTrue(hasattr(tab, "rename_check"))
        self.assertTrue(hasattr(tab, "test_mode_check"))
        self.assertTrue(hasattr(tab, "test_files_spin"))
        self.assertTrue(hasattr(tab, "scan_btn"))

    def test_add_directory(self):
        """Test adding a directory"""
        tab = self.ScanTab(None)
        # Mock FindString on ListBox (which is still MagicMock by default from mock_wx)
        tab.source_list.FindString.return_value = mock_wx.NOT_FOUND

        tab.add_directory("/path/to/music")

        tab.source_list.Append.assert_called_with("/path/to/music")

    def test_add_directory_duplicate(self):
        """Test adding a duplicate directory"""
        tab = self.ScanTab(None)
        tab.source_list.FindString.return_value = 0

        tab.add_directory("/path/to/music")

        tab.source_list.Append.assert_not_called()

    def test_remove_source(self):
        """Test removing a source directory"""
        tab = self.ScanTab(None)
        tab.source_list.GetSelection.return_value = 0

        event = MagicMock()
        tab.on_remove_source(event)

        tab.source_list.Delete.assert_called_with(0)

    def test_remove_source_none_selected(self):
        """Test removing when nothing is selected"""
        tab = self.ScanTab(None)
        tab.source_list.GetSelection.return_value = mock_wx.NOT_FOUND

        event = MagicMock()
        tab.on_remove_source(event)

        tab.source_list.Delete.assert_not_called()

    def test_get_options(self):
        """Test retrieving options from UI"""
        tab = self.ScanTab(None)

        tab.rename_check.SetValue(True)
        tab.extensions_edit.SetValue("mp3,wav")
        tab.test_mode_check.SetValue(False)
        tab.test_files_spin.SetValue(5)

        options = tab.get_options()

        self.assertEqual(options["rename_files"], True)
        self.assertEqual(options["file_extensions"], ["mp3", "wav"])
        self.assertEqual(options["test_mode"], False)
        self.assertEqual(options["test_file_count"], 5)

    def test_validate_source_directories(self):
        """Test validation logic"""
        tab = self.ScanTab(None)

        tab.source_list.GetCount.return_value = 0
        self.assertFalse(tab.validate_source_directories())
        self.assertTrue(mock_wx.MessageBox.called)

        mock_wx.MessageBox.reset_mock()

        tab.source_list.GetCount.return_value = 1
        self.assertTrue(tab.validate_source_directories())
        self.assertFalse(mock_wx.MessageBox.called)

    def test_collect_source_dirs(self):
        """Test collecting source directories"""
        tab = self.ScanTab(None)
        expected = ["/dir1", "/dir2"]
        tab.source_list.GetStrings.return_value = expected

        self.assertEqual(tab.collect_source_dirs(), expected)

    def test_on_scan_clicked(self):
        """Test scan button click handler"""
        tab = self.ScanTab(None)
        event = MagicMock()

        with patch.object(tab, "validate_source_directories", return_value=True):
            tab.on_scan_clicked(event)
            event.Skip.assert_called()

        event.reset_mock()
        with patch.object(tab, "validate_source_directories", return_value=False):
            tab.on_scan_clicked(event)
            event.Skip.assert_not_called()
