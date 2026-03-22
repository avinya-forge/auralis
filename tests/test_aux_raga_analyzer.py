from unittest.mock import MagicMock, patch

import pytest

# In conftest.py, PyQt6 is heavily mocked, meaning `raga_analyzer.analyze_btn`
# is actually a MagicMock, not a real QPushButton. So we test the mock calls.
from src.modules.aux.raga_analyzer import RagaAnalyzerWidget


@pytest.fixture
def mock_ai_service():
    with patch("src.modules.aux.raga_analyzer.AIService") as mock_service:
        yield mock_service


@pytest.fixture
def raga_analyzer(mock_ai_service):
    widget = RagaAnalyzerWidget()
    # Mocking out PyQt objects since the environment is fully mocked
    widget.analyze_btn = MagicMock()

    widget.result_labels = [MagicMock() for _ in range(3)]
    widget.progress_bars = [MagicMock() for _ in range(3)]
    return widget


def test_initial_state():
    # Because of conftest.py's mocks, we test logic flow
    widget = RagaAnalyzerWidget()
    # It attempts to disable analyze_btn in init
    widget.analyze_btn.setEnabled.assert_called()


def test_set_file(raga_analyzer):
    raga_analyzer.set_file("test.mp3")
    raga_analyzer.analyze_btn.setEnabled.assert_called_with(True)
    assert raga_analyzer.current_file == "test.mp3"

    raga_analyzer.set_file(None)
    raga_analyzer.analyze_btn.setEnabled.assert_called_with(False)
    assert raga_analyzer.current_file is None


@patch("src.modules.aux.raga_analyzer.QMessageBox.warning")
def test_start_analysis_ai_disabled(mock_warning, raga_analyzer):
    raga_analyzer.set_file("test.mp3")
    raga_analyzer.ai_service.check_health = MagicMock(return_value={"enabled": False})

    raga_analyzer.start_analysis()

    mock_warning.assert_called_once()
    assert raga_analyzer.worker is None


@patch("src.modules.aux.raga_analyzer.RagaAnalysisWorker")
def test_start_analysis_ai_enabled(mock_worker_class, raga_analyzer):
    raga_analyzer.set_file("test.mp3")
    raga_analyzer.ai_service.check_health = MagicMock(return_value={"enabled": True})

    mock_worker_instance = MagicMock()
    mock_worker_class.return_value = mock_worker_instance

    raga_analyzer.start_analysis()

    raga_analyzer.analyze_btn.setEnabled.assert_called_with(False)
    raga_analyzer.analyze_btn.setText.assert_called_with("Analyzing...")

    mock_worker_instance.start.assert_called_once()
    assert raga_analyzer.worker == mock_worker_instance


def test_on_analysis_finished_with_results(raga_analyzer):
    mock_result = {
        "ragas": [
            ("Bhairav", 0.95),
            ("Yaman", 0.85),
            ("Todi", 0.75),
            ("Malkauns", 0.60),  # Only top 3 should be shown
        ]
    }

    raga_analyzer.on_analysis_finished(mock_result)

    raga_analyzer.analyze_btn.setEnabled.assert_called_with(True)
    raga_analyzer.analyze_btn.setText.assert_called_with("Analyze Raga")

    raga_analyzer.result_labels[0].setText.assert_called_with("Bhairav: 95%")
    raga_analyzer.result_labels[0].setVisible.assert_called_with(True)
    raga_analyzer.progress_bars[0].setValue.assert_called_with(95)
    raga_analyzer.progress_bars[0].setVisible.assert_called_with(True)

    raga_analyzer.result_labels[1].setText.assert_called_with("Yaman: 85%")
    raga_analyzer.result_labels[1].setVisible.assert_called_with(True)

    raga_analyzer.result_labels[2].setText.assert_called_with("Todi: 75%")
    raga_analyzer.result_labels[2].setVisible.assert_called_with(True)


def test_on_analysis_finished_no_results(raga_analyzer):
    mock_result = {"ragas": []}

    raga_analyzer.on_analysis_finished(mock_result)

    raga_analyzer.analyze_btn.setEnabled.assert_called_with(True)
    raga_analyzer.analyze_btn.setText.assert_called_with("Analyze Raga")

    raga_analyzer.result_labels[0].setText.assert_called_with("No raga detected.")
    raga_analyzer.result_labels[0].setVisible.assert_called_with(True)


@patch("src.modules.aux.raga_analyzer.QMessageBox.critical")
def test_on_analysis_error(mock_critical, raga_analyzer):
    raga_analyzer.on_analysis_error("Test Error")

    raga_analyzer.analyze_btn.setEnabled.assert_called_with(True)
    raga_analyzer.analyze_btn.setText.assert_called_with("Analyze Raga")
    mock_critical.assert_called_once()
