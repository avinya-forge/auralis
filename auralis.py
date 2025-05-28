#!/usr/bin/env python3
"""
Auralis - Music File Management Application
PatternSeekers

Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

# Import configuration first
from src.utils.config import get_config, create_env_example, is_windows, is_macos, is_linux
from src.gui.ui_factory import create_app, create_main_window, set_app_id, get_icon_path

# Set up logging
def setup_logging():
    """Set up logging for the application"""
    # Get log file path from config
    log_file = get_config("ERROR_LOG_FILE", "./error.log")
    verbose = get_config("VERBOSE_LOGGING", False)
    
    # Ensure directory exists
    log_dir = os.path.dirname(os.path.abspath(log_file))
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('auralis')

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    # Required dependencies
    required_deps = [
        "mutagen", "requests", "acoustid", 
        "musicbrainzngs", "psutil", "discogs_client", 
        "PIL", "numpy", "dotenv", "PyQt6"
    ]
    
    for dep in required_deps:
        try:
            if dep == "PIL":
                __import__("PIL")
            elif dep == "dotenv":
                __import__("dotenv")
            else:
                __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"Required dependencies missing: {', '.join(missing_deps)}.\n\n"
              f"Please install all dependencies with:\n"
              f"pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main entry point for the application"""
    # Create example .env file if it doesn't exist
    create_env_example()
    
    # Set up logging
    logger = setup_logging()
    logger.info(f"Starting Auralis on {os.name} platform")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies, exiting")
        sys.exit(1)
    
    # Set application ID on Windows
    set_app_id()
    
    # Create application instance using factory
    app = create_app(sys.argv)
    
    # Set application information
    app.setApplicationName("Auralis")
    app.setOrganizationName("PatternSeekers")
    
    # Create splash screen
    splash = None
    splash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "splash.png")
    
    try:
        if os.path.isfile(splash_path) and os.path.getsize(splash_path) > 0:
            from PyQt6.QtWidgets import QSplashScreen
            from PyQt6.QtGui import QPixmap
            from PyQt6.QtCore import Qt, QTimer
            
            pixmap = QPixmap(splash_path)
            if not pixmap.isNull():
                splash = QSplashScreen(pixmap)
                splash.show()
                splash.showMessage("Loading Auralis...", 
                                 Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                                 Qt.GlobalColor.white)
                app.processEvents()
    except Exception as e:
        logger.warning(f"Could not load splash screen: {str(e)}")
    
    # Create main window using factory
    window = create_main_window()
    
    # Show main window
    if splash:
        QTimer.singleShot(1500, lambda: (splash.finish(window), window.show()))
    else:
        window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 