"""
Auralis - wxPython Main Window Implementation
"""

import os
from typing import Any, Dict, List, Optional

import wx  # type: ignore

try:
    import wx.adv  # type: ignore
except ImportError:
    pass

from src.gui.wx.events import EVT_COMPLETED, EVT_FILE, EVT_PROGRESS, EVT_STATUS
from src.gui.wx.tabs.metadata_tab import MetadataTab
from src.gui.wx.tabs.organize_tab import OrganizeTab
from src.gui.wx.tabs.scan_tab import ScanTab
from src.gui.wx.worker import WorkerThread
from src.utils.config import get_config
from src.utils.system_utils import SystemMonitor


class AuralisTaskBarIcon(wx.adv.TaskBarIcon):
    """TaskBarIcon implementation for system tray support"""

    def __init__(self, frame: wx.Frame) -> None:
        super().__init__()
        self.frame = frame
        self._set_icon()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def _set_icon(self) -> None:
        """Set the taskbar icon"""
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "resources",
            "icons",
            "auralis.png",
        )
        if os.path.exists(icon_path):
            icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ANY)
            self.SetIcon(icon, "Auralis")

    def CreatePopupMenu(self) -> wx.Menu:
        """Create the popup menu for the taskbar icon"""
        menu = wx.Menu()
        restore_item = menu.Append(wx.ID_ANY, "Restore")
        exit_item = menu.Append(wx.ID_EXIT, "Exit")

        self.Bind(wx.EVT_MENU, self.on_restore, restore_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        return menu

    def on_left_down(self, event: Any) -> None:
        """Handle left click on taskbar icon"""
        self.on_restore(event)

    def on_restore(self, event: Any) -> None:
        """Restore the main window"""
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def on_exit(self, event: Any) -> None:
        """Exit the application"""
        self.frame.Close()


class MainWindow(wx.Frame):
    """
    Main window for the Auralis application - wxPython implementation.

    This class orchestrates the GUI components, including tabs for scanning,
    organizing, and metadata editing, as well as the progress tracking and
    worker thread management.
    """

    def __init__(self) -> None:
        """Initialize the main window and its components."""
        super().__init__(
            parent=None,
            title="Auralis - Music File Management",
            size=(1200, 800),
        )

        # Worker thread
        self.worker: Optional[WorkerThread] = None

        # Set window icon
        self._set_icon()

        # Initialize components
        self.system_monitor = SystemMonitor()

        # Load default directories
        self.default_input_dir = str(get_config("DEFAULT_INPUT_DIR", ""))
        self.default_output_dir = str(get_config("DEFAULT_OUTPUT_DIR", ""))

        # Start system monitoring
        self.system_monitor.start_monitoring()

        # Setup UI
        self._init_ui()

        # Center on screen
        self.Center()

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_ICONIZE, self.on_iconize)

        # Initialize TaskBarIcon
        self.task_bar_icon: Optional[AuralisTaskBarIcon] = None
        try:
            self.task_bar_icon = AuralisTaskBarIcon(self)
        except Exception:
            # Fallback if TaskBarIcon fails or not supported
            pass

        # Bind worker events
        self.Bind(EVT_PROGRESS, self.on_progress)
        self.Bind(EVT_STATUS, self.on_status)
        self.Bind(EVT_FILE, self.on_file)
        self.Bind(EVT_COMPLETED, self.on_completed)

    def _set_icon(self) -> None:
        """Set the application window icon."""
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

    def _init_ui(self) -> None:
        """Initialize the user interface components and layout."""
        # Create Menu Bar
        self._create_menu()

        # Create Status Bar
        self.CreateStatusBar(2)
        self.SetStatusWidths([-1, 100])
        self.SetStatusText("Ready", 0)

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
        self.stop_btn.Disable()  # Disable stop initially

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

        # Bind Button Events
        self.run_btn.Bind(wx.EVT_BUTTON, self.on_run_clicked)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_clicked)

        # Bind Tab Buttons (they propagate up or use Skip())
        self.scan_tab.scan_btn.Bind(wx.EVT_BUTTON, self.on_scan_only)
        self.organize_tab.organize_btn.Bind(wx.EVT_BUTTON, self.on_organize_only)
        self.organize_tab.dry_run_btn.Bind(wx.EVT_BUTTON, self.on_organize_dry_run)

        # Check if MetadataTab has a button
        if hasattr(self.metadata_tab, "update_btn"):
            self.metadata_tab.update_btn.Bind(wx.EVT_BUTTON, self.on_metadata_only)

    def _create_menu(self) -> None:
        """Create the application menu bar."""
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

    def on_exit(self, event: Any) -> None:
        """
        Handle exit menu item selection.

        Args:
            event (Any): The wxPython event object.
        """
        self.Close()

    def on_about(self, event: Any) -> None:
        """
        Handle about menu item selection.

        Args:
            event (Any): The wxPython event object.
        """
        wx.MessageBox(
            "Auralis\n\nAdvanced Music File Management\n\nDeveloped by PatternSeekers",
            "About Auralis",
            wx.OK | wx.ICON_INFORMATION,
        )

    def on_close(self, event: Any) -> None:
        """
        Handle window close event.

        Args:
            event (Any): The wxPython event object.
        """
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            # Give it a moment to stop
            self.worker.join(0.5)

        # Stop system monitoring
        if hasattr(self, "system_monitor"):
            self.system_monitor.stop_monitoring()

        # Remove taskbar icon
        if hasattr(self, "task_bar_icon") and self.task_bar_icon:
            self.task_bar_icon.RemoveIcon()
            self.task_bar_icon.Destroy()

        event.Skip()

    def on_iconize(self, event: Any) -> None:
        """Handle window minimization"""
        if event.IsIconized():
            # Only hide if we have a tray icon to restore from
            if self.task_bar_icon:
                self.Hide()
        else:
            self.Show()
        event.Skip()

    def set_ai_processing_active(self, active: bool) -> None:
        """Toggle the AI processing indicator in the status bar"""
        if active:
            self.SetStatusText("🧠 AI Active", 1)
        else:
            self.SetStatusText("", 1)

    # --- Worker Control ---

    def start_worker(
        self,
        start_stage: int = 1,
        end_stage: int = 3,
        active_stages: Optional[List[int]] = None,
        dry_run: bool = False,
    ) -> None:
        """
        Start the worker thread with specified stage configuration.

        Args:
            start_stage (int): The starting stage number.
            end_stage (int): The ending stage number.
            active_stages (Optional[List[int]]): List of specific stages to run.
            dry_run (bool): Whether to run in dry-run mode (no changes).
        """
        if self.worker and self.worker.is_alive():
            wx.MessageBox("Processing is already in progress.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        # Collect inputs
        source_dirs = self.scan_tab.collect_source_dirs()
        if not source_dirs:
            wx.MessageBox(
                "Please add at least one source directory in the Scan tab.",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )
            return

        dest_dir = self.organize_tab.get_destination()
        if not dest_dir or dest_dir == "No destination selected":
            # Destination is only strictly required for Organize stage (Stage 2)
            # Check if Stage 2 is in active stages
            is_organize_active = False
            if active_stages:
                if 2 in active_stages:
                    is_organize_active = True
            elif start_stage <= 2 and end_stage >= 2:
                is_organize_active = True

            if is_organize_active:
                wx.MessageBox(
                    "Please select a destination directory in the Organize tab.",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
                return
            dest_dir = ""  # Optional otherwise

        # Collect options
        options: Dict[str, Any] = {}
        options.update(self.scan_tab.get_options())
        options.update(self.organize_tab.get_options())
        options.update(self.metadata_tab.get_options())

        # Additional options
        limit_files = None
        if options.get("test_mode"):
            limit_files = options.get("test_file_count")

        # UI Updates
        self.run_btn.Disable()
        self.stop_btn.Enable()
        self.scan_tab.scan_btn.Disable()
        self.organize_tab.organize_btn.Disable()
        self.organize_tab.dry_run_btn.Disable()
        if hasattr(self.metadata_tab, "update_btn"):
            self.metadata_tab.update_btn.Disable()

        self.progress_bar.SetValue(0)
        self.log_text.Clear()
        self.file_list.Clear()

        # Start Worker
        self.worker = WorkerThread(
            window=self,
            source_dirs=source_dirs,
            dest_dir=dest_dir,
            options=options,
            system_monitor=self.system_monitor,
            limit_files=limit_files,
            dry_run=dry_run,
            start_stage=start_stage,
            end_stage=end_stage,
            active_stages=active_stages,
        )
        self.worker.start()

    def on_run_clicked(self, event: Any) -> None:
        """
        Handle 'Run All Stages' button click.

        Args:
            event (Any): The wxPython event object.
        """
        self.start_worker(start_stage=1, end_stage=3)

    def on_scan_only(self, event: Any) -> None:
        """
        Handle 'Scan Only' button click.

        Args:
            event (Any): The wxPython event object.
        """
        if self.scan_tab.validate_source_directories():
            self.start_worker(start_stage=1, end_stage=1)

    def on_organize_only(self, event: Any) -> None:
        """
        Handle 'Organize Only' button click.

        Args:
            event (Any): The wxPython event object.
        """
        if self.scan_tab.validate_source_directories() and self.organize_tab.validate_destination():
            self.start_worker(start_stage=1, end_stage=2)

    def on_organize_dry_run(self, event: Any) -> None:
        """
        Handle 'Dry Run' button click.

        Args:
            event (Any): The wxPython event object.
        """
        if self.scan_tab.validate_source_directories() and self.organize_tab.validate_destination():
            self.start_worker(start_stage=1, end_stage=2, dry_run=True)

    def on_metadata_only(self, event: Any) -> None:
        """
        Handle 'Metadata Only' button click.

        Args:
            event (Any): The wxPython event object.
        """
        if self.scan_tab.validate_source_directories():
            self.start_worker(active_stages=[1, 3])

    def on_stop_clicked(self, event: Any) -> None:
        """
        Handle 'Stop Processing' button click.

        Args:
            event (Any): The wxPython event object.
        """
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.log_text.AppendText("Stopping...\n")
            self.stop_btn.Disable()

    # --- Event Handlers ---

    def on_progress(self, event: Any) -> None:
        """
        Handle worker progress update events.

        Args:
            event (Any): The custom progress event.
        """
        # event.stage, event.current, event.total
        if event.total > 0:
            percent = int((event.current / event.total) * 100)
            self.progress_bar.SetValue(percent)

        self.stage_label.SetLabel(f"Stage: {event.stage} ({event.current}/{event.total})")

    def on_status(self, event: Any) -> None:
        """
        Handle worker status update events.

        Args:
            event (Any): The custom status event.
        """
        self.SetStatusText(event.message, 0)
        self.log_text.AppendText(f"{event.message}\n")

    def on_file(self, event: Any) -> None:
        """
        Handle worker file update events.

        Args:
            event (Any): The custom file event.
        """
        self.current_file_label.SetLabel(os.path.basename(event.file_path))
        # Add to listbox if it's a new file event (like found file)
        # But we get many file events.
        # For now just update label.

    def on_completed(self, event: Any) -> None:
        """
        Handle worker completion events.

        Args:
            event (Any): The custom completion event.
        """
        self.run_btn.Enable()
        self.stop_btn.Disable()
        self.scan_tab.scan_btn.Enable()
        self.organize_tab.organize_btn.Enable()
        self.organize_tab.dry_run_btn.Enable()
        if hasattr(self.metadata_tab, "update_btn"):
            self.metadata_tab.update_btn.Enable()

        results = event.results
        if results.get("success"):
            wx.MessageBox(
                f"Processing completed successfully.\nProcessed {results.get('files_processed')} files.",
                "Completed",
                wx.OK | wx.ICON_INFORMATION,
            )
        else:
            wx.MessageBox(
                f"Processing failed: {results.get('error')}",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

        self.worker = None
