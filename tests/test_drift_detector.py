import logging
from unittest.mock import patch

from src.utils.ai.drift_detector import DriftDetector


def test_drift_detector_initialization():
    detector = DriftDetector(kl_threshold=0.8)
    assert detector.kl_threshold == 0.8
    assert detector.reference_distribution == {}


def test_set_reference_distribution():
    detector = DriftDetector()
    dist = {"class_a": 10, "class_b": 10}
    detector.set_reference_distribution(dist)

    assert detector.reference_distribution["class_a"] == 0.5
    assert detector.reference_distribution["class_b"] == 0.5


def test_set_reference_distribution_empty():
    detector = DriftDetector()
    dist = {"class_a": 0, "class_b": 0}
    detector.set_reference_distribution(dist)
    assert detector.reference_distribution == {}


def test_analyze_drift_no_reference(caplog):
    detector = DriftDetector()
    with caplog.at_level(logging.WARNING):
        result = detector.analyze_drift({"class_a": 1.0})

    assert result["drift_detected"] is False
    assert result["kl_divergence"] == 0.0
    assert "No reference distribution set" in caplog.text


def test_analyze_drift_empty_current(caplog):
    detector = DriftDetector()
    detector.set_reference_distribution({"class_a": 1.0})

    with caplog.at_level(logging.ERROR):
        result = detector.analyze_drift({"class_a": 0.0})

    assert result["drift_detected"] is False
    assert result["kl_divergence"] == 0.0
    assert "Current distribution is empty" in caplog.text


def test_analyze_drift_no_drift():
    detector = DriftDetector(kl_threshold=0.5)
    detector.set_reference_distribution({"class_a": 0.5, "class_b": 0.5})

    # Same distribution shouldn't trigger drift
    result = detector.analyze_drift({"class_a": 50, "class_b": 50})
    assert result["drift_detected"] is False
    assert result["kl_divergence"] < 0.5


@patch.object(DriftDetector, "trigger_retraining")
def test_analyze_drift_with_drift(mock_trigger, caplog):
    detector = DriftDetector(kl_threshold=0.5)
    detector.set_reference_distribution({"class_a": 0.9, "class_b": 0.1})

    with caplog.at_level(logging.WARNING):
        # Very different distribution should trigger drift
        result = detector.analyze_drift({"class_a": 0.1, "class_b": 0.9, "class_c": 0.1})

    assert result["drift_detected"] is True
    assert result["kl_divergence"] > 0.5
    assert "Model drift detected" in caplog.text
    mock_trigger.assert_called_once()


def test_trigger_retraining(caplog):
    detector = DriftDetector()
    with caplog.at_level(logging.INFO):
        detector.trigger_retraining()

    assert "Triggering automated model retraining pipeline" in caplog.text


def test_analyze_drift_history():
    detector = DriftDetector(kl_threshold=0.5, history_size=2)
    detector.set_reference_distribution({"class_a": 0.9, "class_b": 0.1})

    # First drift - shouldn't trigger because avg_kl won't be > 0.5 yet
    detector.analyze_drift({"class_a": 0.1, "class_b": 0.9, "class_c": 0.1})

    # It might trigger on first if the single divergence is high enough and makes avg_kl > 0.5
    # Let's ensure a steady state first
    detector.kl_history = [0.1, 0.1]

    result2 = detector.analyze_drift({"class_a": 0.1, "class_b": 0.9, "class_c": 0.1})
    assert result2["historical_avg_kl"] > 0
