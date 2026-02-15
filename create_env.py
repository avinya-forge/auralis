import os
import shutil
import requests
import zipfile

# Environment variables
ENV_EXAMPLE_PATH = ".env.example"
ENV_PATH = ".env"
REQUIRED_VARS = {
    "UI_FRAMEWORK": "pyqt6",
    "MUSIC_DIR": "",
    "OUTPUT_DIR": "",
    "ACOUSTID_API_KEY": "",
    "DISCOGS_TOKEN": ""
}


def create_env_file():
    """Create .env file from .env.example or with default values"""
    if os.path.exists(ENV_PATH):
        print(f"{ENV_PATH} already exists.")
        return

    if os.path.exists(ENV_EXAMPLE_PATH):
        print(f"Creating {ENV_PATH} from {ENV_EXAMPLE_PATH}...")
        shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)
    else:
        print(f"Creating {ENV_PATH} with default values...")
        with open(ENV_PATH, "w") as f:
            for key, value in REQUIRED_VARS.items():
                f.write(f"{key}={value}\n")

    print(f"{ENV_PATH} created successfully.")
    print("Please edit the file and add your API keys.")


if __name__ == "__main__":
    create_env_file()
