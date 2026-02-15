import os
import shutil


def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("Created .env file from .env.example")
        else:
            print("Error: .env.example not found")
    else:
        print(".env file already exists")


if __name__ == "__main__":
    create_env_file()
