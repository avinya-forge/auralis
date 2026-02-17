"""
Auralis - wxPython Main Window Implementation
"""

import os

import wx  # type: ignore

from src.gui.wx.tabs.metadata_tab import MetadataTab
from src.gui.wx.tabs.organize_tab import OrganizeTab
from src.gui.wx.tabs.scan_tab import ScanTab
from src.utils.config import get_config
from src.utils.system_utils import SystemMonitor


class MainWindow(wx.Frame):
    """Main window for the Auralis application - wxPython implementation"""

    def __init__(self):
        super().__init__(
            parent=None,
            title="Auralis - Music File Management",
            size=(1200, 800),
        )

        # Set window icon
        self._set_icon()

        # Initialize components
        self.system_monitor = SystemMonitor()

        # Load default directories
        self.default_input_dir = get_config("DEFAULT_INPUT_DIR", "")
        self.default_output_dir = get_config("DEFAULT_OUTPUT_DIR", "")

        # Start system monitoring
        self.system_monitor.start_monitoring()

        # Setup UI
        self._init_ui()

        # Center on screen
        self.Center()

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _set_icon(self):
        """Set the application icon"""
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "resources",
            "icons",
            "auralis.png",
        )
        if os.path.exists(icon_path):
            # wx.Icon location, type
            # Try to determine type from extension or just use BITMAP_TYPE_ANY
            icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ANY)
            self.SetIcon(icon)

    def _init_ui(self):
        """Initialize the user interface"""
        # Create Menu Bar
        self._create_menu()

        # Create Status Bar
        self.CreateStatusBar()
        self.SetStatusText("Ready")

        # Main Panel
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        header_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        header_text = wx.StaticText(panel, label="Auralis")
        header_text.SetFont(header_font)
        main_sizer.Add(header_text, 0, wx.ALL, 10)

        # Main Splitter
        self.splitter = wx.SplitterWindow(panel)

        # Left Panel: File List
        self.left_panel = wx.Panel(self.splitter)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        file_list_label = wx.StaticText(self.left_panel, label="File List")
        file_list_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        file_list_label.SetFont(file_list_font)
        left_sizer.Add(file_list_label, 0, wx.ALL, 5)

        self.file_list = wx.ListBox(self.left_panel)
        left_sizer.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 5)

        # File Details
        file_details_label = wx.StaticText(self.left_panel, label="File Details")
        file_details_font = wx.Font(
            10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        file_details_label.SetFont(file_details_font)
        left_sizer.Add(file_details_label, 0, wx.TOP | wx.LEFT, 5)

        self.file_details = wx.TextCtrl(self.left_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.file_details.SetMinSize((-1, 150))
        left_sizer.Add(self.file_details, 0, wx.EXPAND | wx.ALL, 5)

        self.left_panel.SetSizer(left_sizer)

        # Right Panel: Controls and Tabs
        self.right_panel = wx.Panel(self.splitter)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Notebook (Tabs)
        self.notebook = wx.Notebook(self.right_panel)

        # Add Tabs
        self.scan_tab = ScanTab(self.notebook)
        self.notebook.AddPage(self.scan_tab, "Stage 1: Scan & Rename")

        self.organize_tab = OrganizeTab(self.notebook, default_output_dir=self.default_output_dir)
        self.notebook.AddPage(self.organize_tab, "Stage 2: Organize")

        self.metadata_tab = MetadataTab(self.notebook)
        self.notebook.AddPage(self.metadata_tab, "Stage 3: Metadata")

        right_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Process Controls Group
        sb = wx.StaticBox(self.right_panel, label="Process Control")
        process_sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)

        # Progress
        progress_sizer = wx.BoxSizer(wx.HORIZONTAL)
        progress_sizer.Add(
            wx.StaticText(self.right_panel, label="Progress:"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            5,
        )
        self.progress_bar = wx.Gauge(self.right_panel)
        progress_sizer.Add(self.progress_bar, 1, wx.EXPAND)
        process_sizer.Add(progress_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Labels
        self.stage_label = wx.StaticText(self.right_panel, label="Ready")
        process_sizer.Add(self.stage_label, 0, wx.ALL, 2)

        self.current_file_label = wx.StaticText(self.right_panel, label="No file being processed")
        process_sizer.Add(self.current_file_label, 0, wx.ALL, 2)

        # Log
        process_sizer.Add(
            wx.StaticText(self.right_panel, label="Processing Log:"), 0, wx.TOP | wx.LEFT, 5
        )
        self.log_text = wx.TextCtrl(self.right_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        process_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.run_btn = wx.Button(self.right_panel, label="Run All Stages")
        self.stop_btn = wx.Button(self.right_panel, label="Stop Processing")

        btn_sizer.Add(self.run_btn, 1, wx.RIGHT, 5)
        btn_sizer.Add(self.stop_btn, 1)

        process_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        right_sizer.Add(process_sizer, 1, wx.EXPAND | wx.ALL, 5)

        self.right_panel.SetSizer(right_sizer)

        # Split the window
        self.splitter.SplitVertically(self.left_panel, self.right_panel, 600)
        self.splitter.SetMinimumPaneSize(200)

        main_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)

    def _create_menu(self):
        """Create the menu bar"""
        menubar = wx.MenuBar()

        # File Menu
        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, "Exit", "Exit application")
        menubar.Append(file_menu, "&File")

        # Help Menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "About", "About Auralis")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

        # Bind events
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        """Handle exit menu item"""
        self.Close()

    def on_about(self, event):
        """Handle about menu item"""
        wx.MessageBox(
            "Auralis\n\nAdvanced Music File Management\n\nDeveloped by PatternSeekers",
            "About Auralis",
            wx.OK | wx.ICON_INFORMATION,
        )

    def on_close(self, event):
        """Handle window close event"""
        # Stop system monitoring
        if hasattr(self, "system_monitor"):
            self.system_monitor.stop_monitoring()

        event.Skip()
