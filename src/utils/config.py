"""
Auralis - Configuration Utility Module
"""

import json
import os
import platform
from typing import Any, Dict, Optional

from dotenv import load_dotenv  # type: ignore

# Platform detection
PLATFORM: str = platform.system().lower()
IS_WINDOWS: bool = PLATFORM == "windows"
IS_MACOS: bool = PLATFORM == "darwin"
IS_LINUX: bool = PLATFORM == "linux"

# Define configuration defaults
DEFAULT_CONFIG: Dict[str, Any] = {
    # AcoustID/MusicBrainz API
    "ACOUSTID_API_KEY": "1vOwZtEn",  # Default public key, limited usage
    # Discogs API
    "DISCOGS_CONSUMER_KEY": "RZdEfCsofXBPZDLXkKHr",
    "DISCOGS_CONSUMER_SECRET": "AmqQvwMQzTJHVhxHtTUVLHlyeKGcldYh",
    "DISCOGS_REQUEST_TOKEN_URL": "https://api.discogs.com/oauth/request_token",
    "DISCOGS_AUTHORIZE_URL": "https://www.discogs.com/oauth/authorize",
    "DISCOGS_ACCESS_TOKEN_URL": "https://api.discogs.com/oauth/access_token",
    # File paths (platform-specific defaults)
    "DEFAULT_INPUT_DIR": "",
    "DEFAULT_OUTPUT_DIR": "",
    # UI Configuration - PyQt6 is the only supported framework now
    "UI_FRAMEWORK": "pyqt6",
    "WINDOW_WIDTH": 1200,
    "WINDOW_HEIGHT": 800,
    "FULLSCREEN": False,
    "THEME": "system",  # Options: "system", "light", "dark"
    # Processing Settings
    "MAX_THREADS": 4,
    "AUTO_ADJUST_THREADS": True,
    "UI_UPDATE_INTERVAL_MS": 500,
    "OPTIMIZE_SYSTEM": True,
    # File Organization Settings
    "ORGANIZE_BY_LANGUAGE": True,
    "USE_AUDIO_LANGUAGE_DETECTION": True,
    "DETECT_AUDIO_SIMILARITY": True,
    "KEEP_ALL_DUPLICATES": False,
    "HANDLE_DUPLICATES": True,
    "RENAME_FILES": True,
    "REMOVE_EMPTY_DIRS": True,
    "SAVE_ORIGINAL_NAMES": True,
    # File Scanner Settings
    "FILE_EXTENSIONS": "mp3,flac,m4a,wav,aac,ogg,wma,aiff",
    "EXCLUDE_PATTERNS": "System Volume Information,Windows,$Recycle.Bin,tmp,temp,.git,.vscode,node_modules,.idea",
    "MAX_SCAN_DEPTH": 10,
    # Cache Settings
    "ENABLE_CACHE": True,
    "CACHE_DIRECTORY": "./cache",
    "CACHE_EXPIRY_DAYS": 30,
    # Metadata Settings
    "USE_MUSICBRAINZ": True,
    "USE_DISCOGS": True,
    "FETCH_LYRICS": True,
    "SOURCE_PRIORITY": "auto",  # Options: "auto", "musicbrainz_first", "discogs_first"
    # Error Handling
    "ERROR_LOG_FILE": "./error.log",
    "VERBOSE_LOGGING": False,
    # Test Mode
    "TEST_MODE_ENABLED": True,
    "TEST_MODE_FILE_COUNT": 10,
    # AI Configuration
    "AI_ENABLED": True,
    "AI_DEVICE": "auto",
    "AI_SIMULATION_MODE": False,
    "AI_MODEL_CACHE_DIR": "",  # Empty means use default
    "AI_USE_FP16": True,
}

# Set platform-specific defaults
if IS_WINDOWS:
    DEFAULT_CONFIG.update(
        {
            "DEFAULT_INPUT_DIR": os.path.expanduser("~\\Music"),
            "DEFAULT_OUTPUT_DIR": os.path.expanduser("~\\Music\\Organized"),
            "CACHE_DIRECTORY": os.path.expanduser("~\\AppData\\Local\\Auralis\\cache"),
        }
    )
elif IS_MACOS:
    DEFAULT_CONFIG.update(
        {
            "DEFAULT_INPUT_DIR": os.path.expanduser("~/Music"),
            "DEFAULT_OUTPUT_DIR": os.path.expanduser("~/Music/Organized"),
            "CACHE_DIRECTORY": os.path.expanduser("~/Library/Caches/Auralis"),
        }
    )
elif IS_LINUX:
    DEFAULT_CONFIG.update(
        {
            "DEFAULT_INPUT_DIR": os.path.expanduser("~/Music"),
            "DEFAULT_OUTPUT_DIR": os.path.expanduser("~/Music/Organized"),
            "CACHE_DIRECTORY": os.path.expanduser("~/.cache/auralis"),
        }
    )

# Application directories
APP_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR: str = os.path.join(APP_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# File paths for configuration
ENV_FILE_PATH: str = os.path.join(APP_DIR, ".env")
CONFIG_FILE_PATH: str = os.path.join(DATA_DIR, "config.json")


class Config:
    """
    Configuration manager that loads settings from .env file,
    config.json, or uses defaults.

    Implements the Singleton pattern.
    """

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls) -> "Config":
        """
        Singleton pattern to ensure only one instance of Config exists.

        Returns:
            Config: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from various sources in order of precedence."""
        # Start with defaults
        self._config = DEFAULT_CONFIG.copy()

        self._load_json_config()
        self._load_env_config()

    def _load_json_config(self) -> None:
        """
        Try to load from JSON config file.
        Overrides defaults if found.
        """
        try:
            if os.path.exists(CONFIG_FILE_PATH):
                with open(CONFIG_FILE_PATH, "r") as f:
                    json_config = json.load(f)
                    for key, value in json_config.items():
                        if value is not None:  # Only override if value is not None
                            self._config[key] = value
        except Exception as e:
            print(f"Warning: Could not load config.json: {str(e)}")

    def _load_env_config(self) -> None:
        """
        Try to load from .env file (highest precedence).
        Overrides JSON config and defaults if found.
        """
        try:
            # Load from .env file if it exists
            if os.path.exists(ENV_FILE_PATH):
                load_dotenv(ENV_FILE_PATH)

            # Override with environment variables
            for key in self._config.keys():
                env_value = os.getenv(key)
                if env_value:
                    self._set_env_value(key, env_value)
        except Exception as e:
            print(f"Warning: Could not load .env file: {str(e)}")

    def _set_env_value(self, key: str, env_value: str) -> None:
        """
        Set a configuration value from an environment variable string,
        converting types as necessary.

        Args:
            key (str): The configuration key.
            env_value (str): The value from the environment variable.
        """
        # Convert types appropriately
        current_value = self._config.get(key)
        if isinstance(current_value, bool):
            self._config[key] = env_value.lower() in ("true", "yes", "1", "on")
        elif isinstance(current_value, int):
            try:
                self._config[key] = int(env_value)
            except ValueError:
                pass
        else:
            self._config[key] = env_value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with optional default.

        Args:
            key (str): The configuration key.
            default (Any, optional): The default value if the key is not found.

        Returns:
            Any: The configuration value.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key (str): The configuration key.
            value (Any): The value to set.
        """
        self._config[key] = value

    def save(self) -> bool:
        """
        Save the current configuration to config.json.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)

            with open(CONFIG_FILE_PATH, "w") as f:
                json.dump(self._config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
            return False

    def create_env_example(self) -> bool:
        """
        Create an example .env file.

        Returns:
            bool: True if successful, False otherwise.
        """
        example_path = os.path.join(APP_DIR, ".env.example")
        try:
            with open(example_path, "w") as f:
                f.write("# Auralis Environment Configuration Example\n")
                f.write("# Copy this file to .env and fill in your actual API keys\n\n")

                # Group settings by category
                categories = {
                    "API Keys": [
                        "ACOUSTID_API_KEY",
                        "DISCOGS_CONSUMER_KEY",
                        "DISCOGS_CONSUMER_SECRET",
                        "DISCOGS_REQUEST_TOKEN_URL",
                        "DISCOGS_AUTHORIZE_URL",
                        "DISCOGS_ACCESS_TOKEN_URL",
                    ],
                    "File Paths": ["DEFAULT_INPUT_DIR", "DEFAULT_OUTPUT_DIR"],
                    "UI Configuration": ["WINDOW_WIDTH", "WINDOW_HEIGHT", "FULLSCREEN", "THEME"],
                    "Processing Settings": [
                        "MAX_THREADS",
                        "AUTO_ADJUST_THREADS",
                        "UI_UPDATE_INTERVAL_MS",
                        "OPTIMIZE_SYSTEM",
                    ],
                    "File Organization": [
                        "ORGANIZE_BY_LANGUAGE",
                        "USE_AUDIO_LANGUAGE_DETECTION",
                        "DETECT_AUDIO_SIMILARITY",
                        "KEEP_ALL_DUPLICATES",
                        "HANDLE_DUPLICATES",
                        "RENAME_FILES",
                        "REMOVE_EMPTY_DIRS",
                        "SAVE_ORIGINAL_NAMES",
                    ],
                    "File Scanner": ["FILE_EXTENSIONS", "EXCLUDE_PATTERNS", "MAX_SCAN_DEPTH"],
                    "Cache Settings": ["ENABLE_CACHE", "CACHE_DIRECTORY", "CACHE_EXPIRY_DAYS"],
                    "Metadata Settings": [
                        "USE_MUSICBRAINZ",
                        "USE_DISCOGS",
                        "FETCH_LYRICS",
                        "SOURCE_PRIORITY",
                    ],
                    "Error Handling": ["ERROR_LOG_FILE", "VERBOSE_LOGGING"],
                    "Test Mode": ["TEST_MODE_ENABLED", "TEST_MODE_FILE_COUNT"],
                }

                # Write each category
                for category, keys in categories.items():
                    f.write(f"\n# {category}\n")
                    for key in keys:
                        value = self._config.get(key, "")
                        if key.endswith("_KEY") or key.endswith("_SECRET"):
                            f.write(f"{key}=your_{key.lower()}_here\n")
                        else:
                            f.write(f"{key}={value}\n")

            return True
        except Exception as e:
            print(f"Error creating .env.example: {str(e)}")
            return False

    @property
    def platform(self) -> str:
        """Get the current platform"""
        return PLATFORM

    @property
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return IS_WINDOWS

    @property
    def is_macos(self) -> bool:
        """Check if running on macOS"""
        return IS_MACOS

    @property
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return IS_LINUX


# Initialize the config
config = Config()

# Export functions for easy access


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value"""
    return config.get(key, default)


def set_config(key: str, value: Any) -> None:
    """Set a configuration value"""
    config.set(key, value)


def save_config() -> bool:
    """Save the current configuration"""
    return config.save()


def create_env_example() -> bool:
    """Create an example .env file"""
    return config.create_env_example()


def get_platform() -> str:
    """Get the current platform"""
    return config.platform


def is_windows() -> bool:
    """Check if running on Windows"""
    return config.is_windows


def is_macos() -> bool:
    """Check if running on macOS"""
    return config.is_macos


def is_linux() -> bool:
    """Check if running on Linux"""
    return config.is_linux
