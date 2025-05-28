#!/usr/bin/env python3
"""
Script to create a .env file for Auralis
"""

import os

def create_env_file():
    """Create a .env file with basic configuration"""
    env_content = """# Auralis Configuration

# UI Configuration
UI_FRAMEWORK=pyqt6
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800

# API Keys
ACOUSTID_API_KEY=1vOwZtEn
DISCOGS_CONSUMER_KEY=RZdEfCsofXBPZDLXkKHr
DISCOGS_CONSUMER_SECRET=AmqQvwMQzTJHVhxHtTUVLHlyeKGcldYh

# File Organization Settings
ORGANIZE_BY_LANGUAGE=true
HANDLE_DUPLICATES=true
RENAME_FILES=true
"""
    
    # Write the .env file
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("Created .env file successfully")
        return True
    except Exception as e:
        print(f"Error creating .env file: {str(e)}")
        return False

if __name__ == "__main__":
    create_env_file() 