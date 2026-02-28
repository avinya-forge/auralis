"""
Stage 3: Metadata Tab (wxPython)
"""

from typing import Any, Dict, Optional

import wx  # type: ignore

from src.gui.wx.dialogs.api_keys_dialog import APIKeysDialog
from src.utils.config import get_config



class AIPanel(wx.Panel):
    """Panel for AI Analysis options"""
    def __init__(self, parent: Optional[wx.Window] = None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        sizer = wx.BoxSizer(wx.VERTICAL)

        # AI Options
        ai_sb = wx.StaticBox(self, label="AI Analysis (Neural Audio)")
        ai_sizer = wx.StaticBoxSizer(ai_sb, wx.VERTICAL)

        self.ai_analyze_check = wx.CheckBox(self, label="Enable AI Analysis")
        self.ai_analyze_check.SetValue(bool(get_config("USE_AI_ANALYSIS", False)))
        self.ai_analyze_check.SetToolTip("Use deep learning to analyze Raga, Mood, and Genre")
        ai_sizer.Add(self.ai_analyze_check, 0, wx.ALL, 5)

        ai_info = wx.StaticText(
            self,
            label="Note: AI analysis requires significant system resources."
        )
        ai_info.Wrap(400)
        ai_sizer.Add(ai_info, 0, wx.ALL, 5)

        sizer.Add(ai_sizer, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)

    def get_options(self) -> Dict[str, Any]:
        return {
            "use_ai_analysis": self.ai_analyze_check.GetValue()
        }

class MetadataTab(wx.Panel):
    """Tab for Stage 3: Metadata"""

    def __init__(self, parent: Optional[wx.Window] = None) -> None:
        super().__init__(parent)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI"""
        main_v_sizer = wx.BoxSizer(wx.VERTICAL)
        main_h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left Panel (Options)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # Metadata sources
        metadata_sb = wx.StaticBox(self, label="Metadata Sources")
        metadata_sizer = wx.StaticBoxSizer(metadata_sb, wx.VERTICAL)

        # MusicBrainz / AcoustID
        self.mb_check = wx.CheckBox(self, label="MusicBrainz / AcoustID")
        self.mb_check.SetValue(bool(get_config("USE_MUSICBRAINZ", True)))
        metadata_sizer.Add(self.mb_check, 0, wx.ALL, 5)

        # Discogs
        self.discogs_check = wx.CheckBox(self, label="Discogs")
        self.discogs_check.SetValue(bool(get_config("USE_DISCOGS", True)))
        metadata_sizer.Add(self.discogs_check, 0, wx.ALL, 5)

        # Spotify
        self.spotify_check = wx.CheckBox(self, label="Spotify (Requires API Keys)")
        self.spotify_check.SetValue(bool(get_config("USE_SPOTIFY", False)))
        metadata_sizer.Add(self.spotify_check, 0, wx.ALL, 5)

        # Last.fm
        self.lastfm_check = wx.CheckBox(self, label="Last.fm (Requires API Keys)")
        self.lastfm_check.SetValue(bool(get_config("USE_LASTFM", False)))
        metadata_sizer.Add(self.lastfm_check, 0, wx.ALL, 5)

        # Configure API Keys Button
        self.config_keys_btn = wx.Button(self, label="Configure API Keys")
        self.config_keys_btn.Bind(wx.EVT_BUTTON, self.on_configure_api_keys)
        metadata_sizer.Add(self.config_keys_btn, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        left_sizer.Add(metadata_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Lyrics options
        lyrics_sb = wx.StaticBox(self, label="Lyrics")
        lyrics_sizer = wx.StaticBoxSizer(lyrics_sb, wx.VERTICAL)

        # Fetch lyrics
        self.lyrics_check = wx.CheckBox(self, label="Fetch and Embed Lyrics")
        self.lyrics_check.SetValue(bool(get_config("FETCH_LYRICS", True)))
        self.lyrics_check.SetToolTip(
            "Fetch lyrics from online sources and embed them in the audio files"
        )
        lyrics_sizer.Add(self.lyrics_check, 0, wx.ALL, 5)

        lyrics_info = wx.StaticText(
            self,
            label="Lyrics will be embedded in the audio files so they can be "
            "displayed in music players like Apple Music.",
        )
        lyrics_info.Wrap(400)  # Wrap text
        lyrics_sizer.Add(lyrics_info, 0, wx.ALL, 5)


        left_sizer.Add(lyrics_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # AI Panel
        self.ai_panel = AIPanel(self)
        left_sizer.Add(self.ai_panel, 0, wx.EXPAND | wx.ALL, 5)

        main_h_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 0)

        # Right Panel (Preview)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        preview_sb = wx.StaticBox(self, label="Cover Art Preview")
        preview_sizer = wx.StaticBoxSizer(preview_sb, wx.VERTICAL)

        # StaticBitmap for image
        self.cover_art_preview = wx.StaticBitmap(self, size=(200, 200))
        # Optional: Set a border or background
        try:
            self.cover_art_preview.SetBackgroundColour(wx.Colour(50, 50, 50))
        except Exception:
            pass

        preview_sizer.Add(self.cover_art_preview, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        right_sizer.Add(preview_sizer, 0, wx.EXPAND | wx.ALL, 5)

        main_h_sizer.Add(right_sizer, 0, wx.EXPAND | wx.ALL, 0)

        main_v_sizer.Add(main_h_sizer, 1, wx.EXPAND)

        # Update button
        self.update_btn = wx.Button(self, label="Update Metadata")
        self.update_btn.Bind(wx.EVT_BUTTON, self.on_update_clicked)
        main_v_sizer.Add(self.update_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(main_v_sizer)

    def on_configure_api_keys(self, event: Any) -> None:
        """Open the API Keys configuration dialog"""
        dlg = APIKeysDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            wx.MessageBox(
                "API keys saved for current session.",
                "Configuration Saved",
                wx.OK | wx.ICON_INFORMATION,
            )
        dlg.Destroy()

    def on_update_clicked(self, event: Any) -> None:
        """Handle update button click"""
        # Allow event to propagate
        event.Skip()

    def set_cover_art(self, image_path: str) -> None:
        """Set the cover art preview image"""
        try:
            if image_path:
                img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
                # Scale to fit 200x200
                width = img.GetWidth()
                height = img.GetHeight()
                max_size = 200
                if width > max_size or height > max_size:
                    aspect = width / height
                    if width > height:
                        new_width = max_size
                        new_height = int(max_size / aspect)
                    else:
                        new_height = max_size
                        new_width = int(max_size * aspect)
                    img = img.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)

                self.cover_art_preview.SetBitmap(wx.Bitmap(img))
            else:
                # Clear or set placeholder
                self.cover_art_preview.SetBitmap(wx.NullBitmap)
        except Exception:
            # Log error?
            pass

    def get_options(self) -> Dict[str, Any]:
        """Get options relevant to this tab"""
        options = {
            "use_musicbrainz": self.mb_check.GetValue(),
            "use_discogs": self.discogs_check.GetValue(),
            "use_spotify": self.spotify_check.GetValue(),
            "use_lastfm": self.lastfm_check.GetValue(),
            "fetch_lyrics": self.lyrics_check.GetValue(),
        }
        options.update(self.ai_panel.get_options())
        return options
