import unittest

try:
    from src.gui.pyqt.tabs.validation_tab import ValidationTab
except ImportError:
    ValidationTab = None  # type: ignore


class TestValidationTabMethods(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
