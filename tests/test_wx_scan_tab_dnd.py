import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx module
mock_wx = MagicMock()

# Mock FileDropTarget


class MockFileDropTarget:
    def __init__(self, data=None):
        pass

    def OnDropFiles(self, x, y, filenames):
        pass


mock_wx.FileDropTarget = MockFileDropTarget

# Mock Panel as a class


class MockPanel:
    def __init__(self, parent=None, **kwargs):
        pass

    def SetSizer(self, sizer):
        pass

    def Bind(self, event, handler):
        pass


mock_wx.Panel = MockPanel

# Mock Widget Helper to swallow arguments and avoid MagicMock(spec=parent)


def MockWidget(parent=None, *args, **kwargs):
    return MagicMock()


# Mock other wx classes using MockWidget where parent is passed
mock_wx.ListBox = MockWidget
mock_wx.BoxSizer = MockWidget
mock_wx.StaticBox = MockWidget
mock_wx.StaticBoxSizer = MockWidget
mock_wx.StaticText = MockWidget
mock_wx.Button = MockWidget
mock_wx.CheckBox = MockWidget
mock_wx.TextCtrl = MockWidget
mock_wx.SpinCtrl = MockWidget

# MessageBox and DirDialog are usually called as functions or classes
mock_wx.MessageBox = MagicMock()
mock_wx.DirDialog = MagicMock

# Constants
mock_wx.VERTICAL = 1
mock_wx.HORIZONTAL = 2
mock_wx.EXPAND = 8
mock_wx.ALL = 16
mock_wx.RIGHT = 32
mock_wx.ALIGN_CENTER_VERTICAL = 512
mock_wx.ALIGN_CENTER = 1024
mock_wx.ID_OK = 5100
mock_wx.DD_DEFAULT_STYLE = 1
mock_wx.DD_DIR_MUST_EXIST = 2
mock_wx.NOT_FOUND = -1
mock_wx.ICON_WARNING = 100
mock_wx.OK = 4


class TestScanTabDnD(unittest.TestCase):
    def setUp(self):
        # Patch sys.modules to inject our mock_wx
        self.modules_patcher = patch.dict(sys.modules, {"wx": mock_wx})
        self.modules_patcher.start()

        # Reload the module under test
        if "src.gui.wx.tabs.scan_tab" in sys.modules:
            del sys.modules["src.gui.wx.tabs.scan_tab"]

        import src.gui.wx.tabs.scan_tab

        self.module = src.gui.wx.tabs.scan_tab
        self.ScanTab = self.module.ScanTab
        self.FileDropTarget = self.module.FileDropTarget

        # Patch os.path.isdir
        self.isdir_patcher = patch("os.path.isdir")
        self.mock_isdir = self.isdir_patcher.start()

        # Patch get_config
        self.config_patcher = patch("src.gui.wx.tabs.scan_tab.get_config")
        self.mock_get_config = self.config_patcher.start()
        self.mock_get_config.return_value = True  # Default

    def tearDown(self):
        self.config_patcher.stop()
        self.isdir_patcher.stop()
        self.modules_patcher.stop()

    def test_file_drop_target(self):
        """Test FileDropTarget logic"""
        callback = MagicMock()
        target = self.FileDropTarget(callback)

        filenames = ["/path/1", "/path/2"]
        target.OnDropFiles(0, 0, filenames)

        callback.assert_called_with(filenames)

    def test_handle_dropped_files(self):
        """Test handling of dropped files in ScanTab"""
        tab = self.ScanTab(None)

        filenames = ["/dir1", "/file1.mp3", "/dir2"]

        # Mock isdir behavior
        def side_effect(path):
            return path.startswith("/dir")

        self.mock_isdir.side_effect = side_effect

        # Mock add_directory
        tab.add_directory = MagicMock()

        tab.handle_dropped_files(filenames)

        # Should only call add_directory for directories
        self.assertEqual(tab.add_directory.call_count, 2)
        tab.add_directory.assert_any_call("/dir1")
        tab.add_directory.assert_any_call("/dir2")


if __name__ == "__main__":
    unittest.main()
