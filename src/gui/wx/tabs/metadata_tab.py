"""
Stage 3: Metadata Tab (wxPython)
"""

import wx  # type: ignore

from src.utils.config import get_config


class MetadataTab(wx.Panel):
    """Tab for Stage 3: Metadata"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Metadata sources
        metadata_sb = wx.StaticBox(self, label="Metadata Sources")
        metadata_sizer = wx.StaticBoxSizer(metadata_sb, wx.VERTICAL)

        # MusicBrainz / AcoustID
        self.mb_check = wx.CheckBox(self, label="MusicBrainz / AcoustID")
        self.mb_check.SetValue(get_config("USE_MUSICBRAINZ", True))
        metadata_sizer.Add(self.mb_check, 0, wx.ALL, 5)

        # Discogs
        self.discogs_check = wx.CheckBox(self, label="Discogs")
        self.discogs_check.SetValue(get_config("USE_DISCOGS", True))
        metadata_sizer.Add(self.discogs_check, 0, wx.ALL, 5)

        main_sizer.Add(metadata_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Lyrics options
        lyrics_sb = wx.StaticBox(self, label="Lyrics")
        lyrics_sizer = wx.StaticBoxSizer(lyrics_sb, wx.VERTICAL)

        # Fetch lyrics
        self.lyrics_check = wx.CheckBox(self, label="Fetch and Embed Lyrics")
        self.lyrics_check.SetValue(get_config("FETCH_LYRICS", True))
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

        main_sizer.Add(lyrics_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Update button
        self.update_btn = wx.Button(self, label="Update Metadata")
        self.update_btn.Bind(wx.EVT_BUTTON, self.on_update_clicked)
        main_sizer.Add(self.update_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def on_update_clicked(self, event):
        """Handle update button click"""
        # Allow event to propagate
        event.Skip()

    def get_options(self):
        """Get options relevant to this tab"""
        return {
            "use_musicbrainz": self.mb_check.GetValue(),
            "use_discogs": self.discogs_check.GetValue(),
            "fetch_lyrics": self.lyrics_check.GetValue(),
        }
