"""
Auralis - wxPython API Keys Dialog
"""

import os
from typing import Any, Dict, List, Optional

import wx


class APIKeysDialog(wx.Dialog):
    """Dialog for configuring API keys"""

    def __init__(self, parent: Optional[wx.Window] = None) -> None:
        super().__init__(parent, title="Configure API Keys", size=(500, 600))

        self.inputs: Dict[str, Any] = {}
        self.scrolled_panel: Optional[wx.ScrolledWindow] = None
        self.init_ui()
        self.CenterOnParent()

    def init_ui(self) -> None:
        """Initialize the UI"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Scrolled Panel for content
        self.scrolled_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.scrolled_panel.SetScrollRate(0, 20)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # AcoustID Section
        self._add_api_section(
            self.scrolled_panel,
            panel_sizer,
            "AcoustID",
            ["ACOUSTID_API_KEY"],
            "Required for audio fingerprinting.",
            "https://acoustid.org/login",
        )

        # Discogs Section
        self._add_api_section(
            self.scrolled_panel,
            panel_sizer,
            "Discogs",
            ["DISCOGS_TOKEN"],
            "Required for Discogs metadata.",
            "https://www.discogs.com/settings/developers",
        )

        # Spotify Section
        self._add_api_section(
            self.scrolled_panel,
            panel_sizer,
            "Spotify",
            ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET"],
            "Required for Spotify metadata.",
            "https://developer.spotify.com/dashboard",
        )

        # Last.fm Section
        self._add_api_section(
            self.scrolled_panel,
            panel_sizer,
            "Last.fm",
            ["LASTFM_API_KEY", "LASTFM_API_SECRET"],
            "Required for Last.fm metadata.",
            "https://www.last.fm/api/account/create",
        )

        self.scrolled_panel.SetSizer(panel_sizer)
        main_sizer.Add(self.scrolled_panel, 1, wx.EXPAND | wx.ALL, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        save_btn = wx.Button(self, wx.ID_OK, label="Save")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel")

        btn_sizer.Add(save_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(cancel_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def _add_api_section(
        self,
        parent: wx.Window,
        sizer: wx.Sizer,
        title: str,
        keys: List[str],
        description: str,
        url: str,
    ) -> None:
        """Add a section for an API"""
        sb = wx.StaticBox(parent, label=title)
        box_sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)

        # Description with Link
        desc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        desc_text = wx.StaticText(parent, label=description)
        desc_sizer.Add(desc_text, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        link_btn = wx.Button(parent, label="Get Key", size=(-1, 25))
        # Note: We can't type check lambda properly here easily, but it's fine
        link_btn.Bind(wx.EVT_BUTTON, lambda evt: wx.LaunchDefaultBrowser(url))
        desc_sizer.Add(link_btn, 0, wx.LEFT, 10)

        box_sizer.Add(desc_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Inputs
        for key in keys:
            self._add_input_row(parent, box_sizer, key)

        sizer.Add(box_sizer, 0, wx.EXPAND | wx.BOTTOM, 15)

    def _add_input_row(self, parent: wx.Window, sizer: wx.Sizer, key: str) -> None:
        """Add a label and text input for a key"""
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Format label (e.g., SPOTIPY_CLIENT_ID -> Client ID)
        if "_" in key:
            # Handle special cases or generic rule
            parts = key.split("_")
            # e.g. SPOTIPY_CLIENT_ID -> Client Id
            # Remove first part (prefix)
            label_text = " ".join(parts[1:]).title()
            if not label_text:  # Fallback
                label_text = key
        else:
            label_text = key

        label = wx.StaticText(parent, label=f"{label_text}:", size=(120, -1))
        row_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        # Input
        current_value = os.environ.get(key, "")
        text_ctrl = wx.TextCtrl(parent, value=current_value)
        row_sizer.Add(text_ctrl, 1, wx.EXPAND)

        sizer.Add(row_sizer, 0, wx.EXPAND | wx.BOTTOM, 5)

        # Store reference
        self.inputs[key] = text_ctrl

    def on_save(self, event: Any) -> None:
        """Handle save button click"""
        # Save to environment variables for current session
        for key, text_ctrl in self.inputs.items():
            value = text_ctrl.GetValue().strip()
            if value:
                os.environ[key] = value
            elif key in os.environ:
                # Remove empty keys if they exist
                del os.environ[key]

        # Close dialog with OK code
        event.Skip()
