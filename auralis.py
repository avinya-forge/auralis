"""
Auralis - Music Organizer and Metadata Manager
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication

from src.utils.config import get_config
from src.gui.ui_factory import UIFactory


def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("auralis.log", mode='w')
        ]
    )


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()

    # Load configuration
    config_loaded = get_config("VERSION", "0.1.0")
    logging.info(f"Starting Auralis v{config_loaded}")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Auralis")
    app.setOrganizationName("PatternSeekers")

    # Set application icon if available
    icon_path = UIFactory.get_icon_path("auralis.png")
    if icon_path:
        # Implementation depends on UI framework
        pass

    # Create and show main window
    try:
        window = UIFactory.create_main_window()
        window.show()

        # Start event loop
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
