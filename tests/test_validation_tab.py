import unittest
from unittest.mock import MagicMock

from src.gui.pyqt.tabs.validation_tab import ValidationTab


class TestValidationTab(unittest.TestCase):
    def test_verify_record_emits_signal_and_updates_dict(self):
        # Using unbound method approach to avoid QApplication init
        mock_self = MagicMock()
        mock_self.current_record = {"file_id": "123"}

        # Call method directly
        ValidationTab.verify_record(mock_self)

        # Verify the record was updated
        self.assertTrue(mock_self.current_record.get("validated"))
        self.assertEqual(mock_self.current_record.get("points_earned"), 10)

        # Verify signal was emitted
        mock_self.metadata_verified.emit.assert_called_once_with("123", mock_self.current_record)

        # Verify layout was cleared
        mock_self._clear_layout.assert_called_once()

    def test_skip_record(self):
        mock_self = MagicMock()
        ValidationTab.skip_record(mock_self)
        mock_self._clear_layout.assert_called_once()

    def test_clear_layout(self):
        mock_self = MagicMock()

        mock_layout = MagicMock()
        mock_self.container_layout = mock_layout
        mock_layout.count.return_value = 2

        mock_item1 = MagicMock()
        mock_widget1 = MagicMock()
        mock_item1.widget.return_value = mock_widget1

        mock_item2 = MagicMock()
        mock_widget2 = MagicMock()
        mock_item2.widget.return_value = mock_widget2

        mock_layout.itemAt.side_effect = [mock_item1, mock_item2]

        mock_self.skip_btn = MagicMock()
        mock_self.verify_btn = MagicMock()

        ValidationTab._clear_layout(mock_self)

        mock_widget1.setParent.assert_called_once_with(None)
        mock_widget2.setParent.assert_called_once_with(None)
        mock_self.skip_btn.setEnabled.assert_called_once_with(False)
        mock_self.verify_btn.setEnabled.assert_called_once_with(False)


if __name__ == "__main__":
    unittest.main()
