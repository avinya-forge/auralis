from src.gui.pyqt.tabs.validation_tab import ValidationTab


def test_validation_tab_init():
    t = ValidationTab()
    assert t.header.text() == "Metadata Validation Queue"
    assert t.scroll_area is not None


def test_load_record():
    t = ValidationTab()
    record = {"raw_tags": {"title": "Song A", "artist": "Artist X"}}
    t.load_record(record)
    assert t.skip_btn.isEnabled()
    assert t.verify_btn.isEnabled()
