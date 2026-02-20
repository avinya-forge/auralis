"""
Unit tests for create_env.py
"""

import create_env
import sys
import os
import unittest
from unittest.mock import patch

# Ensure root directory is in sys.path
sys.path.append(os.getcwd())


class TestCreateEnv(unittest.TestCase):

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("builtins.print")
    def test_create_env_success(self, mock_print, mock_copy, mock_exists):
        """Test creating .env when it doesn't exist but example does"""
        # .env does not exist, .env.example exists
        def exists_side_effect(path):
            if path == ".env":
                return False
            if path == ".env.example":
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        create_env.create_env_file()

        mock_copy.assert_called_with(".env.example", ".env")
        mock_print.assert_called_with("Created .env file from .env.example")

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("builtins.print")
    def test_env_already_exists(self, mock_print, mock_copy, mock_exists):
        """Test when .env already exists"""
        mock_exists.return_value = True

        create_env.create_env_file()

        mock_copy.assert_not_called()
        mock_print.assert_called_with(".env file already exists")

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("builtins.print")
    def test_example_missing(self, mock_print, mock_copy, mock_exists):
        """Test when .env.example is missing"""
        mock_exists.return_value = False

        create_env.create_env_file()

        mock_copy.assert_not_called()
        mock_print.assert_called_with("Error: .env.example not found")


if __name__ == "__main__":
    unittest.main()
