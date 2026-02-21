"""
Stage 1: Scan & Rename Tab (wxPython)
"""

from typing import Any, Dict, List, Optional

import wx  # type: ignore

from src.utils.config import get_config


class ScanTab(wx.Panel):
    """Tab for Stage 1: Scan & Rename"""

    def __init__(self, parent: Optional[wx.Window] = None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Source directory selection
        source_sb = wx.StaticBox(self, label="Source Directories")
        source_sizer = wx.StaticBoxSizer(source_sb, wx.VERTICAL)

        self.source_list = wx.ListBox(self)
        source_sizer.Add(self.source_list, 1, wx.EXPAND | wx.ALL, 5)

        source_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_source_btn = wx.Button(self, label="Add Directory")
        self.add_source_btn.Bind(wx.EVT_BUTTON, self.on_add_source)
        self.remove_source_btn = wx.Button(self, label="Remove Selected")
        self.remove_source_btn.Bind(wx.EVT_BUTTON, self.on_remove_source)

        source_btn_sizer.Add(self.add_source_btn, 0, wx.RIGHT, 5)
        source_btn_sizer.Add(self.remove_source_btn, 0)
        source_sizer.Add(source_btn_sizer, 0, wx.ALL, 5)

        main_sizer.Add(source_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Scan options
        options_sb = wx.StaticBox(self, label="Scan Options")
        options_sizer = wx.StaticBoxSizer(options_sb, wx.VERTICAL)

        # File extensions
        ext_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ext_sizer.Add(
            wx.StaticText(self, label="File Extensions:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5
        )
        self.extensions_edit = wx.TextCtrl(
            self, value=str(get_config("FILE_EXTENSIONS", "mp3,flac,m4a,wav,aac,ogg,wma"))
        )
        ext_sizer.Add(self.extensions_edit, 1, wx.EXPAND)
        options_sizer.Add(ext_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Rename options
        self.rename_check = wx.CheckBox(self, label="Rename Files (Title - Artist format)")
        self.rename_check.SetValue(bool(get_config("RENAME_FILES", True)))
        options_sizer.Add(self.rename_check, 0, wx.ALL, 5)

        # Test mode
        self.test_mode_check = wx.CheckBox(self, label="Test Mode (Process only a subset of files)")
        self.test_mode_check.SetValue(bool(get_config("TEST_MODE_ENABLED", True)))
        options_sizer.Add(self.test_mode_check, 0, wx.ALL, 5)

        # Number of test files
        test_files_sizer = wx.BoxSizer(wx.HORIZONTAL)
        test_files_sizer.Add(
            wx.StaticText(self, label="Number of test files:"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            5,
        )
        self.test_files_spin = wx.SpinCtrl(
            self, min=1, max=100, initial=int(get_config("TEST_MODE_FILE_COUNT", 10))
        )
        test_files_sizer.Add(self.test_files_spin, 0)
        options_sizer.Add(test_files_sizer, 0, wx.ALL, 5)

        main_sizer.Add(options_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Scan button
        self.scan_btn = wx.Button(self, label="Scan Only")
        self.scan_btn.Bind(wx.EVT_BUTTON, self.on_scan_clicked)
        main_sizer.Add(self.scan_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def on_add_source(self, event: Any) -> None:
        """Add a source directory to scan"""
        dlg = wx.DirDialog(
            self, "Select Source Directory", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.add_directory(dlg.GetPath())
        dlg.Destroy()

    def add_directory(self, path: str) -> None:
        """Add a directory path to the list"""
        if self.source_list.FindString(path) == wx.NOT_FOUND:
            self.source_list.Append(path)

    def on_remove_source(self, event: Any) -> None:
        """Remove the selected source directory"""
        selection = self.source_list.GetSelection()
        if selection != wx.NOT_FOUND:
            self.source_list.Delete(selection)

    def on_scan_clicked(self, event: Any) -> None:
        """Handle scan button click"""
        if self.validate_source_directories():
            # Notify parent or allow event to bubble up if handled there
            # Since we don't have custom signals like pyqtSignal easily without pubsub,
            # we rely on the parent binding to this button or checking the object.
            # But to be clean, we can post a custom event if we wanted to.
            # For now, let's just let the event propagate.
            event.Skip()

    def validate_source_directories(self) -> bool:
        """Validate that source directories are selected"""
        if self.source_list.GetCount() == 0:
            wx.MessageBox(
                "Please add at least one source directory.",
                "Missing Source",
                wx.OK | wx.ICON_WARNING,
            )
            return False
        return True

    def collect_source_dirs(self) -> List[str]:
        """Collect all source directories from the list"""
        return list(self.source_list.GetStrings())

    def get_options(self) -> Dict[str, Any]:
        """Get options relevant to this tab"""
        return {
            "rename_files": self.rename_check.GetValue(),
            "file_extensions": self.extensions_edit.GetValue().split(","),
            "test_mode": self.test_mode_check.GetValue(),
            "test_file_count": self.test_files_spin.GetValue(),
        }
