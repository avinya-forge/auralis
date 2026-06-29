import unittest
from unittest.mock import MagicMock, patch

from src.gui.pyqt.tabs.validation_tab import ValidationTab


class TestValidationTabMethods(unittest.TestCase):
    @patch("src.services.gamification.GamificationService")
    def test_methods_via_unbound(self, mock_gamification):
        # Setup mocks
        mock_gamification_instance = mock_gamification.return_value
        mock_gamification_instance.get_user_stats.return_value = {
            "level": 1,
            "points": 10,
            "validations": 1,
        }
        mock_gamification_instance.add_validation_points.return_value = {
            "level": 2,
            "points": 100,
            "validations": 10,
        }

        # We need a mock tab to pass to unbound methods since we can't easily instantiate a real one
        tab_mock = MagicMock()
        tab_mock.gamification_service = mock_gamification_instance
        tab_mock.user_id = "test_user"
        tab_mock.current_record = {"file_id": "file_1"}

        # Test _on_skip
        ValidationTab._on_skip(tab_mock)
        tab_mock.metadata_skipped.emit.assert_called_with("file_1")
        self.assertIsNone(tab_mock.current_record)

        # Test update_stats_display
        ValidationTab.update_stats_display(tab_mock)
        tab_mock.stats_label.setText.assert_called_with("Level: 1 | Points: 10 | Validations: 1")

        # Test _on_verify
        tab_mock.current_record = {"file_id": "file_2"}
        tab_mock.container_layout.count.return_value = 0
        ValidationTab._on_verify(tab_mock)
        tab_mock.metadata_verified.emit.assert_called_with("file_2", {})
        tab_mock.update_stats_display.assert_called()


if __name__ == "__main__":
    unittest.main()
