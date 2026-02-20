import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock wx module
mock_wx = MagicMock()


class MockDialog:
    def __init__(self, parent=None, **kwargs):
        pass

    def CenterOnParent(self):
        pass

    def SetSizer(self, sizer):
        pass

    def Bind(self, event, handler):
        pass


mock_wx.Dialog = MockDialog
# Constants
mock_wx.VERTICAL = 1
mock_wx.HORIZONTAL = 2
mock_wx.VSCROLL = 4
mock_wx.EXPAND = 8
mock_wx.ALL = 16
mock_wx.RIGHT = 32
mock_wx.LEFT = 64
mock_wx.BOTTOM = 128
mock_wx.ALIGN_RIGHT = 256
mock_wx.ALIGN_CENTER_VERTICAL = 512
mock_wx.ID_OK = 5100
mock_wx.ID_CANCEL = 5101
mock_wx.EVT_BUTTON = 10001


class TestAPIKeysDialog(unittest.TestCase):
    def setUp(self):
        # Patch sys.modules
        self.modules_patcher = patch.dict(sys.modules, {"wx": mock_wx})
        self.modules_patcher.start()

        # Reload module
        if "src.gui.wx.dialogs.api_keys_dialog" in sys.modules:
            del sys.modules["src.gui.wx.dialogs.api_keys_dialog"]

        import src.gui.wx.dialogs.api_keys_dialog

        self.APIKeysDialog = src.gui.wx.dialogs.api_keys_dialog.APIKeysDialog

        mock_wx.reset_mock()
        mock_wx.TextCtrl.reset_mock()

        # Clean env
        self.original_environ = os.environ.copy()
        self.keys = [
            "ACOUSTID_API_KEY",
            "DISCOGS_TOKEN",
            "SPOTIPY_CLIENT_ID",
            "SPOTIPY_CLIENT_SECRET",
            "LASTFM_API_KEY",
            "LASTFM_API_SECRET",
        ]
        for key in self.keys:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        self.modules_patcher.stop()
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_init_creates_inputs(self):
        parent = MagicMock()
        dialog = self.APIKeysDialog(parent)

        for key in self.keys:
            self.assertIn(key, dialog.inputs)
            self.assertIsInstance(dialog.inputs[key], MagicMock)

    def test_init_loads_existing_values(self):
        os.environ["ACOUSTID_API_KEY"] = "existing_key"

        parent = MagicMock()
        self.APIKeysDialog(parent)

        # Check calls to mock_wx.TextCtrl
        found = False
        for call in mock_wx.TextCtrl.call_args_list:
            if call.kwargs.get("value") == "existing_key":
                found = True
                break
        self.assertTrue(
            found,
            f"TextCtrl not initialized with existing key. Calls: {mock_wx.TextCtrl.call_args_list}",
        )

    def test_save_updates_env(self):
        dialog = self.APIKeysDialog(None)

        mock_ctrl = dialog.inputs["ACOUSTID_API_KEY"]
        mock_ctrl.GetValue.return_value = "new_api_key"

        event = MagicMock()
        dialog.on_save(event)

        self.assertEqual(os.environ.get("ACOUSTID_API_KEY"), "new_api_key")
        event.Skip.assert_called_once()

    def test_save_clears_empty_env(self):
        os.environ["ACOUSTID_API_KEY"] = "old_value"

        dialog = self.APIKeysDialog(None)

        mock_ctrl = dialog.inputs["ACOUSTID_API_KEY"]
        mock_ctrl.GetValue.return_value = "   "

        event = MagicMock()
        dialog.on_save(event)

        self.assertNotIn("ACOUSTID_API_KEY", os.environ)

    def test_add_api_section(self):
        dialog = self.APIKeysDialog(None)
        parent = MagicMock()
        sizer = MagicMock()

        dialog._add_api_section(
            parent,
            sizer,
            "Test Title",
            ["TEST_KEY_1", "TEST_KEY_2"],
            "Test Desc",
            "http://example.com",
        )

        self.assertIn("TEST_KEY_1", dialog.inputs)
        self.assertIn("TEST_KEY_2", dialog.inputs)

        self.assertTrue(sizer.Add.called)
