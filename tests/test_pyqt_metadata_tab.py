"""
Unit tests for PyQt6 MetadataTab and AIPanel
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure conftest Mocks for PyQt6 don't cause MagicMock inheritance issues for get_options
class TestPyQtMetadataTab(unittest.TestCase):
    """Test cases for PyQt6 MetadataTab and AIPanel"""

    @patch("src.utils.config.get_config")
    def test_aipanel_init_and_options(self, mock_get_config):
        """Test AIPanel initialization and get_options"""
        def mock_config(key, default=None):
            if key == "USE_AI_ANALYSIS":
                return True
            return default

        mock_get_config.side_effect = mock_config

        from src.gui.pyqt.tabs.metadata_tab import AIPanel
        import sys

        # `AIPanel` inherits from `QGroupBox` which is mocked as `MagicMock` in conftest.
        # This makes `AIPanel` a mock object class, preventing us from running its methods directly.
        # Instead, we fetch the actual function objects from the module dict to test the logic.
        # Because we can't extract `init_ui` directly due to how MagicMock inheritance behaves
        # (the methods get absorbed into the Mock), we can bypass the problem by asserting on
        # what get_options does. But we still need to instantiate it to test it correctly.
        # Since it's essentially just a mock object wrapping a dict we can mock `ai_analyze_check`.

        panel = AIPanel()
        panel.ai_analyze_check = MagicMock()
        panel.ai_analyze_check.isChecked.return_value = True

        # Because `get_options` is also mocked out, we use `patch` to insert a fake class
        # earlier to grab the function logic, or we can just redefine it here as it is extremely simple.
        # Let's extract it from the file directly by reading the source to avoid any MagicMock weirdness
        # or we just rely on testing `MetadataTab` which we already do successfully.

        # For full coverage of AIPanel, we will simply read its attributes
        # Wait, if we want to call the actual method, we need a reference to the un-mocked class.
        pass

        import importlib

        # We temporarily unmock QGroupBox in PyQt6.QtWidgets to let python parse the module normally
        with patch.dict(sys.modules):
            if 'src.gui.pyqt.tabs.metadata_tab' in sys.modules:
                del sys.modules['src.gui.pyqt.tabs.metadata_tab']

            with patch('PyQt6.QtWidgets.QGroupBox', type('QGroupBox', (object,), {})):
                module = importlib.import_module('src.gui.pyqt.tabs.metadata_tab')
                init_ui_func = module.AIPanel.__dict__['init_ui']
                get_options_func = module.AIPanel.__dict__['get_options']

                mock_self = MagicMock()
                with patch('src.gui.pyqt.tabs.metadata_tab.QVBoxLayout'), \
                     patch('src.gui.pyqt.tabs.metadata_tab.QCheckBox') as mock_checkbox_cls, \
                     patch('src.gui.pyqt.tabs.metadata_tab.QLabel'):

                     mock_checkbox_instance = MagicMock()
                     mock_checkbox_cls.return_value = mock_checkbox_instance
                     init_ui_func(mock_self)
                     mock_checkbox_instance.setChecked.assert_called_with(True)

                mock_self.ai_analyze_check.isChecked.return_value = True
                options = get_options_func(mock_self)
                self.assertIn("use_ai_analysis", options)
                self.assertTrue(options["use_ai_analysis"])

                mock_self.ai_analyze_check.isChecked.return_value = False
                options = get_options_func(mock_self)
                self.assertFalse(options["use_ai_analysis"])

    @patch("src.utils.config.get_config")
    def test_metadata_tab_get_options_includes_ai(self, mock_get_config):
        """Test MetadataTab gets options from AIPanel"""
        def mock_config(key, default=None):
            if key == "USE_AI_ANALYSIS":
                return True
            return default

        mock_get_config.side_effect = mock_config

        import sys
        import importlib

        # Similar to AIPanel, we need to temporarily unmock the base class
        # to properly load the logic without global side effects
        with patch.dict(sys.modules):
            if 'src.gui.pyqt.tabs.metadata_tab' in sys.modules:
                del sys.modules['src.gui.pyqt.tabs.metadata_tab']

            # MetadataTab inherits from QWidget
            with patch('PyQt6.QtWidgets.QWidget', type('QWidget', (object,), {})), \
                 patch('PyQt6.QtWidgets.QGroupBox', type('QGroupBox', (object,), {})):

                module = importlib.import_module('src.gui.pyqt.tabs.metadata_tab')
                get_options_func = module.MetadataTab.__dict__['get_options']

                mock_tab = MagicMock()

                mock_tab.mb_check.isChecked.return_value = True
                mock_tab.discogs_check.isChecked.return_value = True
                mock_tab.lyrics_check.isChecked.return_value = False
                mock_tab.cover_art_check.isChecked.return_value = True
                mock_tab.analyze_check.isChecked.return_value = False

                mock_tab.ai_panel.get_options.return_value = {"use_ai_analysis": True}

                options = get_options_func(mock_tab)

                self.assertIn("use_musicbrainz", options)
                self.assertIn("analyze_audio", options)
                self.assertTrue(options["use_musicbrainz"])
                self.assertFalse(options["analyze_audio"])
                self.assertIn("use_ai_analysis", options)
                self.assertTrue(options["use_ai_analysis"])
