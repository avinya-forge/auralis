from unittest.mock import patch

import pytest

from src.utils.perf.latency_logger import LatencyLoggerMiddleware


def test_latency_logger_decorator():
    logger_mw = LatencyLoggerMiddleware()

    @logger_mw
    def sample_func():
        return "success"

    with patch("src.utils.perf.latency_logger.time.time", side_effect=[100.0, 100.05]):
        result = sample_func()

    assert result == "success"


def test_latency_logger_measure_latency():
    logger_mw = LatencyLoggerMiddleware()

    def sample_func(x):
        return x * 2

    with patch("src.utils.perf.latency_logger.time.time", side_effect=[100.0, 100.05]):
        result, latency = logger_mw.measure_latency(sample_func, 5)

    assert result == 10
    assert abs(latency - 50.0) < 0.001  # (100.05 - 100.0) * 1000


def test_latency_logger_measure_latency_exception():
    logger_mw = LatencyLoggerMiddleware()

    def sample_func():
        raise ValueError("Test error")

    with patch("src.utils.perf.latency_logger.time.time", side_effect=[100.0, 100.05]):
        with pytest.raises(ValueError, match="Test error"):
            logger_mw.measure_latency(sample_func)
