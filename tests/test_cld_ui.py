import pytest

from src.modules.cld.ui import CloudSettingsWidget


@pytest.fixture(scope="session")
def qapp():
    return None


def test_cloud_settings_widget_init(qapp):
    widget = CloudSettingsWidget()
    assert widget is not None


def test_cloud_settings_widget_save(qapp):
    widget = CloudSettingsWidget()
    widget._on_save()
