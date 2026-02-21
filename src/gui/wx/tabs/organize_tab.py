"""
Stage 2: Organize Tab (wxPython)
"""

import os
from typing import Any, Dict, Optional

import wx  # type: ignore

from src.utils.config import get_config


class OrganizeTab(wx.Panel):
    """Tab for Stage 2: Organize"""

    def __init__(self, parent: Optional[wx.Window] = None, default_output_dir: str = "") -> None:
        super().__init__(parent)
        self.default_output_dir = default_output_dir
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Destination directory selection
        dest_sb = wx.StaticBox(self, label="Destination Directory")
        dest_sizer = wx.StaticBoxSizer(dest_sb, wx.VERTICAL)

        self.dest_label = wx.StaticText(self, label="No destination selected")
        if self.default_output_dir and os.path.exists(os.path.dirname(self.default_output_dir)):
            self.dest_label.SetLabel(self.default_output_dir)

        dest_sizer.Add(self.dest_label, 0, wx.ALL, 5)

        self.dest_btn = wx.Button(self, label="Select Destination")
        self.dest_btn.Bind(wx.EVT_BUTTON, self.on_select_destination)
        dest_sizer.Add(self.dest_btn, 0, wx.ALL, 5)

        main_sizer.Add(dest_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Organization options
        org_sb = wx.StaticBox(self, label="Organization Options")
        org_sizer = wx.StaticBoxSizer(org_sb, wx.VERTICAL)

        # Language-based organization
        self.lang_org_check = wx.CheckBox(self, label="Organize by Language")
        self.lang_org_check.SetValue(bool(get_config("ORGANIZE_BY_LANGUAGE", True)))
        self.lang_org_check.Bind(wx.EVT_CHECKBOX, self.on_lang_org_toggled)
        org_sizer.Add(self.lang_org_check, 0, wx.ALL, 5)

        # Audio language detection checkbox
        self.audio_lang_detect_check = wx.CheckBox(
            self, label="Use Audio Content for Language Detection"
        )
        self.audio_lang_detect_check.SetValue(True)
        self.audio_lang_detect_check.Enable(self.lang_org_check.GetValue())
        org_sizer.Add(self.audio_lang_detect_check, 0, wx.LEFT | wx.BOTTOM, 20)  # Indent slightly

        # Audio similarity detection
        self.audio_similarity_check = wx.CheckBox(
            self, label="Detect Similar Audio Content (Find Duplicates)"
        )
        self.audio_similarity_check.SetValue(bool(get_config("DETECT_AUDIO_SIMILARITY", True)))
        self.audio_similarity_check.SetToolTip(
            "Analyzes audio content to find duplicate tracks regardless of filename or metadata"
        )
        self.audio_similarity_check.Bind(wx.EVT_CHECKBOX, self.on_similarity_toggled)
        org_sizer.Add(self.audio_similarity_check, 0, wx.ALL, 5)

        # Keep duplicates option
        self.keep_duplicates_check = wx.CheckBox(self, label="Keep All Duplicate Versions")
        self.keep_duplicates_check.SetValue(bool(get_config("KEEP_ALL_DUPLICATES", False)))
        self.keep_duplicates_check.Enable(self.audio_similarity_check.GetValue())
        self.keep_duplicates_check.SetToolTip(
            "If unchecked, only the highest quality version of each duplicate will be kept"
        )
        org_sizer.Add(self.keep_duplicates_check, 0, wx.LEFT | wx.BOTTOM, 20)

        # Duplicate handling
        self.dup_check = wx.CheckBox(self, label="Detect and Handle Duplicates")
        self.dup_check.SetValue(bool(get_config("HANDLE_DUPLICATES", True)))
        org_sizer.Add(self.dup_check, 0, wx.ALL, 5)

        # Remove empty directories
        self.empty_dirs_check = wx.CheckBox(self, label="Remove Empty Directories")
        self.empty_dirs_check.SetValue(bool(get_config("REMOVE_EMPTY_DIRS", True)))
        org_sizer.Add(self.empty_dirs_check, 0, wx.ALL, 5)

        main_sizer.Add(org_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Organize buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dry_run_btn = wx.Button(self, label="Dry Run")
        self.dry_run_btn.Bind(wx.EVT_BUTTON, self.on_dry_run_clicked)
        btn_sizer.Add(self.dry_run_btn, 0, wx.RIGHT, 5)

        self.organize_btn = wx.Button(self, label="Organize Files")
        self.organize_btn.Bind(wx.EVT_BUTTON, self.on_organize_clicked)
        btn_sizer.Add(self.organize_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def on_select_destination(self, event: Any) -> None:
        """Select the destination directory"""
        dlg = wx.DirDialog(self, "Select Destination Directory", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.dest_label.SetLabel(dlg.GetPath())
        dlg.Destroy()

    def on_lang_org_toggled(self, event: Any) -> None:
        """Handle language organization toggle"""
        self.audio_lang_detect_check.Enable(self.lang_org_check.GetValue())

    def on_similarity_toggled(self, event: Any) -> None:
        """Handle audio similarity toggle"""
        self.keep_duplicates_check.Enable(self.audio_similarity_check.GetValue())

    def on_dry_run_clicked(self, event: Any) -> None:
        """Handle dry run button click"""
        if self.validate_destination():
            event.Skip()

    def on_organize_clicked(self, event: Any) -> None:
        """Handle organize button click"""
        if self.validate_destination():
            event.Skip()

    def validate_destination(self) -> bool:
        """Validate that a destination directory is selected"""
        if self.dest_label.GetLabel() == "No destination selected":
            wx.MessageBox(
                "Please select a destination directory.",
                "Missing Destination",
                wx.OK | wx.ICON_WARNING,
            )
            return False
        return True

    def get_destination(self) -> str:
        """Get the selected destination directory"""
        return str(self.dest_label.GetLabel())

    def get_options(self) -> Dict[str, Any]:
        """Get options relevant to this tab"""
        return {
            "organize_by_language": self.lang_org_check.GetValue(),
            "use_audio_language_detection": self.audio_lang_detect_check.GetValue(),
            "detect_audio_similarity": self.audio_similarity_check.GetValue(),
            "keep_all_duplicates": self.keep_duplicates_check.GetValue(),
            "handle_duplicates": self.dup_check.GetValue(),
            "remove_empty_dirs": self.empty_dirs_check.GetValue(),
        }
