import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx module
mock_wx = MagicMock()
mock_wx.adv = MagicMock()

# Mock TaskBarIcon as a class


class MockTaskBarIcon:
    def __init__(self, *args, **kwargs):
        pass

    def SetIcon(self, icon, tooltip):
        pass

    def RemoveIcon(self):
        pass

    def Destroy(self):
        pass

    def Bind(self, event, handler):
        pass


mock_wx.adv.TaskBarIcon = MockTaskBarIcon
mock_wx.adv.EVT_TASKBAR_LEFT_DOWN = MagicMock()

# Mock Frame


class MockFrame:
    def __init__(self, *args, **kwargs):
        self.shown = True
        self.iconized = False

    def SetIcon(self, icon):
        pass

    def Bind(self, event, handler, *args, **kwargs):
        pass

    def Center(self):
        pass

    def CreateStatusBar(self):
        pass

    def SetStatusText(self, text):
        pass

    def SetMenuBar(self, menu_bar):
        pass

    def Close(self):
        pass

    def Hide(self):
        self.shown = False

    def Show(self, show=True):
        self.shown = show

    def Iconize(self, iconize=True):
        self.iconized = iconize

    def IsIconized(self):
        return self.iconized

    def IsShown(self):
        return self.shown

    def Raise(self):
        pass


mock_wx.Frame = MockFrame

# Mock other widgets using MagicMock returning functions


def MockWidget(parent=None, *args, **kwargs):
    return MagicMock()


mock_wx.Panel = MockWidget
mock_wx.BoxSizer = MockWidget
mock_wx.StaticText = MockWidget
mock_wx.SplitterWindow = MockWidget
mock_wx.ListBox = MockWidget
mock_wx.TextCtrl = MockWidget
mock_wx.Notebook = MockWidget
mock_wx.Gauge = MockWidget
mock_wx.Button = MockWidget
mock_wx.StaticBox = MockWidget
mock_wx.StaticBoxSizer = MockWidget
mock_wx.MenuBar = MagicMock()
mock_wx.Menu = MagicMock()
mock_wx.Icon = MagicMock()
mock_wx.MessageBox = MagicMock()

# Constants
mock_wx.VERTICAL = 1
mock_wx.HORIZONTAL = 2
mock_wx.EXPAND = 8
mock_wx.ALL = 16
mock_wx.RIGHT = 32
mock_wx.ALIGN_CENTER_VERTICAL = 512
mock_wx.ALIGN_CENTER = 1024
mock_wx.ID_EXIT = 5001
mock_wx.ID_ABOUT = 5002
mock_wx.ID_ANY = -1
mock_wx.OK = 4
mock_wx.ICON_INFORMATION = 100
mock_wx.TE_MULTILINE = 1
mock_wx.TE_READONLY = 2
mock_wx.BITMAP_TYPE_ANY = 1


class TestTrayIcon(unittest.TestCase):
    def setUp(self):
        # Mock wx.lib.newevent
        mock_wx_lib = MagicMock()
        mock_wx.lib = mock_wx_lib

        # Create a mock for the newevent module
        mock_newevent_module = MagicMock()
        mock_wx_lib.newevent = mock_newevent_module

        # Define NewEvent to return a tuple of 2 mocks
        def mock_new_event():
            return (MagicMock(), MagicMock())

        # Set NewEvent on the module mock.
        # We set it directly as the function
        mock_newevent_module.NewEvent = mock_new_event

        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "wx": mock_wx,
                "wx.adv": mock_wx.adv,
                "wx.lib": mock_wx_lib,
                "wx.lib.newevent": mock_newevent_module,
            },
        )
        self.modules_patcher.start()

        # Patch tabs
        sys.modules["src.gui.wx.tabs.scan_tab"] = MagicMock()
        sys.modules["src.gui.wx.tabs.organize_tab"] = MagicMock()
        sys.modules["src.gui.wx.tabs.metadata_tab"] = MagicMock()

        # Patch worker
        sys.modules["src.gui.wx.worker"] = MagicMock()

        # Patch requests
        sys.modules["requests"] = MagicMock()

        # Reload module
        if "src.gui.wx.main_window" in sys.modules:
            del sys.modules["src.gui.wx.main_window"]

        import src.gui.wx.main_window

        self.module = src.gui.wx.main_window
        self.MainWindow = self.module.MainWindow
        self.AuralisTaskBarIcon = self.module.AuralisTaskBarIcon

        # Mock SystemMonitor
        self.monitor_patcher = patch("src.gui.wx.main_window.SystemMonitor")
        self.monitor_patcher.start()

        # Mock get_config
        self.config_patcher = patch("src.gui.wx.main_window.get_config")
        self.mock_get_config = self.config_patcher.start()
        self.mock_get_config.return_value = ""

    def tearDown(self):
        self.config_patcher.stop()
        self.monitor_patcher.stop()
        self.modules_patcher.stop()

    def test_taskbar_icon_init(self):
        frame = MagicMock()
        icon = self.AuralisTaskBarIcon(frame)

        self.assertEqual(icon.frame, frame)

    def test_restore(self):
        frame = MockFrame()
        frame.Iconize(True)
        frame.Show(False)
        frame.Raise = MagicMock()
        frame.Iconize = MagicMock(side_effect=frame.Iconize)
        frame.Show = MagicMock(side_effect=frame.Show)

        icon = self.AuralisTaskBarIcon(frame)
        icon.on_restore(None)

        frame.Iconize.assert_called_with(False)
        frame.Show.assert_called_with(True)
        frame.Raise.assert_called()

    def test_main_window_integration(self):
        # Instantiate MainWindow
        window = self.MainWindow()

        # Verify task_bar_icon created
        self.assertTrue(hasattr(window, "task_bar_icon"))
        self.assertIsInstance(window.task_bar_icon, self.AuralisTaskBarIcon)

    def test_iconize_event(self):
        window = self.MainWindow()
        event = MagicMock()
        event.IsIconized.return_value = True

        # Spy on Hide/Show
        window.Hide = MagicMock(wraps=window.Hide)
        window.Show = MagicMock(wraps=window.Show)

        window.on_iconize(event)

        window.Hide.assert_called()
        window.Show.assert_not_called()

        event.IsIconized.return_value = False
        window.Hide.reset_mock()
        window.Show.reset_mock()

        window.on_iconize(event)

        window.Show.assert_called()
        window.Hide.assert_not_called()

    def test_iconize_without_tray(self):
        window = self.MainWindow()
        window.task_bar_icon = None
        event = MagicMock()
        event.IsIconized.return_value = True

        window.Hide = MagicMock(wraps=window.Hide)

        window.on_iconize(event)

        # Should NOT hide if no tray icon
        window.Hide.assert_not_called()


if __name__ == "__main__":
    unittest.main()
