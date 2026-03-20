import pytest
from src.modules.neu.ai_config import AIConfig
from src.modules.neu.threshold_filter import ThresholdFilter

def test_aiconfig_singleton():
    config1 = AIConfig()
    config2 = AIConfig()
    assert config1 is config2

    # Change threshold on one, verify the other changes
    config1.confidence_threshold = 0.8
    assert config2.confidence_threshold == 0.8

    # Reset for other tests
    config1.confidence_threshold = 0.65

def test_threshold_filter_default():
    filter_obj = ThresholdFilter()
    tags = [
        {"name": "Rock", "confidence": 0.9},
        {"name": "Jazz", "confidence": 0.6},
        {"name": "Pop", "confidence": 0.65},
        {"name": "NoConfidenceKey"}
    ]

    filtered = filter_obj.filter_tags(tags)

    assert len(filtered) == 3
    assert filtered[0]["name"] == "Rock"
    assert filtered[1]["name"] == "Pop"  # Exactly at threshold 0.65
    assert filtered[2]["name"] == "NoConfidenceKey"

def test_threshold_filter_custom_config():
    config = AIConfig()
    config.confidence_threshold = 0.8

    filter_obj = ThresholdFilter(config)
    tags = [
        {"name": "Rock", "confidence": 0.9},
        {"name": "Jazz", "confidence": 0.79},
        {"name": "Pop", "confidence": 0.8}
    ]

    filtered = filter_obj.filter_tags(tags)

    assert len(filtered) == 2
    assert filtered[0]["name"] == "Rock"
    assert filtered[1]["name"] == "Pop"

    # Reset for global state
    config.confidence_threshold = 0.65
