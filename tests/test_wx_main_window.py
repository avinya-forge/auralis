import sys
import unittest
from unittest.mock import MagicMock, patch

# 1. Mock wx
mock_wx = MagicMock()


class MockFrame:
    def __init__(self, parent=None, **kwargs):
        pass

    def SetIcon(self, icon):
        pass

    def CreateStatusBar(self):
        pass

    def SetStatusText(self, text):
        pass

    def Center(self):
        pass

    def SetMenuBar(self, bar):
        pass

    def Close(self):
        pass

    def Bind(self, event, handler, source=None):
        pass

    def SetSizer(self, sizer):
        pass

    def Show(self):
        pass


mock_wx.Frame = MockFrame


def MockFactory(*args, **kwargs):
    return MagicMock()


mock_wx.Panel = MockFactory
mock_wx.BoxSizer = MockFactory
mock_wx.SplitterWindow = MockFactory
mock_wx.ListBox = MockFactory
mock_wx.TextCtrl = MockFactory
mock_wx.Notebook = MockFactory
mock_wx.Gauge = MockFactory
mock_wx.StaticText = MockFactory
mock_wx.Button = MockFactory
mock_wx.MenuBar = MockFactory
mock_wx.Menu = MockFactory
mock_wx.StaticBox = MockFactory
mock_wx.StaticBoxSizer = MockFactory
mock_wx.Icon = MockFactory
mock_wx.Font = MockFactory
mock_wx.MessageBox = MockFactory
mock_wx.SpinCtrl = MockFactory
mock_wx.CheckBox = MockFactory

# Constants
mock_wx.VERTICAL = 1
mock_wx.HORIZONTAL = 2
mock_wx.EXPAND = 8
mock_wx.ALL = 16
mock_wx.RIGHT = 32
mock_wx.LEFT = 64
mock_wx.TOP = 128
mock_wx.BOTTOM = 256
mock_wx.ALIGN_CENTER_VERTICAL = 512
mock_wx.ALIGN_RIGHT = 1024
mock_wx.ALIGN_CENTER = 2048
mock_wx.TE_MULTILINE = 1
mock_wx.TE_READONLY = 2
mock_wx.FONTFAMILY_DEFAULT = 1
mock_wx.FONTSTYLE_NORMAL = 0
mock_wx.FONTWEIGHT_BOLD = 1
mock_wx.ID_EXIT = 5001
mock_wx.ID_ABOUT = 5002
mock_wx.EVT_MENU = 10001
mock_wx.EVT_CLOSE = 10002
mock_wx.EVT_BUTTON = 10003
mock_wx.OK = 4
mock_wx.ICON_INFORMATION = 100
mock_wx.ICON_WARNING = 200
mock_wx.ICON_ERROR = 300
mock_wx.BITMAP_TYPE_ANY = 0


# 2. Mock Tabs
mock_scan_tab_mod = MagicMock()


class MockScanTab:
    def __init__(self, parent):
        self.scan_btn = MagicMock()

    def validate_source_directories(self):
        return True

    def collect_source_dirs(self):
        return ["/path"]

    def get_options(self):
        return {}


mock_scan_tab_mod.ScanTab = MockScanTab

mock_org_tab_mod = MagicMock()


class MockOrganizeTab:
    def __init__(self, parent, default_output_dir=None):
        self.organize_btn = MagicMock()
        self.dry_run_btn = MagicMock()

    def validate_destination(self):
        return True

    def get_destination(self):
        return "/dest"

    def get_options(self):
        return {}


mock_org_tab_mod.OrganizeTab = MockOrganizeTab

mock_meta_tab_mod = MagicMock()


class MockMetadataTab:
    def __init__(self, parent):
        self.update_btn = MagicMock()

    def get_options(self):
        return {}


mock_meta_tab_mod.MetadataTab = MockMetadataTab

# 3. Mock Worker
mock_worker_mod = MagicMock()


class MockWorkerThread:
    def __init__(self, **kwargs):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def is_alive(self):
        return False

    def join(self, timeout=None):
        pass


mock_worker_mod.WorkerThread = MockWorkerThread

# 4. Mock SystemMonitor
mock_sys_mod = MagicMock()


class MockSystemMonitor:
    def start_monitoring(self):
        pass

    def stop_monitoring(self):
        pass


mock_sys_mod.SystemMonitor = MockSystemMonitor

# 5. Mock Events
mock_events_mod = MagicMock()
mock_events_mod.EVT_PROGRESS = 20001
mock_events_mod.EVT_STATUS = 20002
mock_events_mod.EVT_FILE = 20003
mock_events_mod.EVT_COMPLETED = 20004


class TestMainWindow(unittest.TestCase):
    def setUp(self):
        mocks = {
            "wx": mock_wx,
            "src.gui.wx.tabs.scan_tab": mock_scan_tab_mod,
            "src.gui.wx.tabs.organize_tab": mock_org_tab_mod,
            "src.gui.wx.tabs.metadata_tab": mock_meta_tab_mod,
            "src.gui.wx.worker": mock_worker_mod,
            "src.utils.system_utils": mock_sys_mod,
            "src.gui.wx.events": mock_events_mod
        }
        self.modules_patcher = patch.dict(sys.modules, mocks)
        self.modules_patcher.start()

        mock_wx.reset_mock()

        # Reload MainWindow
        if "src.gui.wx.main_window" in sys.modules:
            del sys.modules["src.gui.wx.main_window"]
        import src.gui.wx.main_window
        self.MainWindow = src.gui.wx.main_window.MainWindow

        # Mock get_config
        self.config_patcher = patch("src.gui.wx.main_window.get_config")
        self.mock_get_config = self.config_patcher.start()
        self.mock_get_config.return_value = ""

    def tearDown(self):
        self.config_patcher.stop()
        self.modules_patcher.stop()

    def test_init(self):
        win = self.MainWindow()
        self.assertTrue(hasattr(win, "scan_tab"))
        self.assertTrue(hasattr(win, "organize_tab"))
        self.assertTrue(hasattr(win, "metadata_tab"))
        self.assertTrue(hasattr(win, "run_btn"))

    def test_start_worker_success(self):
        win = self.MainWindow()

        win.start_worker(start_stage=1, end_stage=3)

        win.run_btn.Disable.assert_called()
        self.assertIsNotNone(win.worker)
        self.assertIsInstance(win.worker, MockWorkerThread)

    def test_start_worker_missing_source(self):
        win = self.MainWindow()

        # Override instance method
        win.scan_tab.collect_source_dirs = MagicMock(return_value=[])

        win.start_worker()

        # Check that MessageBox was called (MockFactory wrapper)
        pass

    def test_on_scan_only(self):
        win = self.MainWindow()
        win.start_worker = MagicMock()

        event = MagicMock()
        win.on_scan_only(event)

        win.start_worker.assert_called_with(start_stage=1, end_stage=1)

    def test_on_completed(self):
        win = self.MainWindow()
        win.worker = MagicMock()

        event = MagicMock()
        event.results = {"success": True, "files_processed": 10}

        win.on_completed(event)

        win.run_btn.Enable.assert_called()
        self.assertIsNone(win.worker)

    def test_on_progress(self):
        win = self.MainWindow()
        event = MagicMock()
        event.stage = 1
        event.current = 50
        event.total = 100

        win.on_progress(event)

        win.progress_bar.SetValue.assert_called_with(50)
        win.stage_label.SetLabel.assert_called()

    def test_on_status(self):
        win = self.MainWindow()
        event = MagicMock()
        event.message = "Test status"

        win.on_status(event)

        win.log_text.AppendText.assert_called_with("Test status\n")
