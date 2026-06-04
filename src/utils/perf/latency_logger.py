import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class LatencyLoggerMiddleware:
    """
    Middleware to track Edge-Cloud roundtrip latency with minimal overhead.
    """

    def __init__(self) -> None:
        pass

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to wrap a function and measure its execution time.
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                logger.info(
                    f"Edge-Cloud roundtrip latency for {func.__name__}: {latency_ms:.2f} ms"
                )

        return wrapper

    def measure_latency(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> tuple[Any, float]:
        """
        Executes the function and returns a tuple of (result, latency_in_ms).
        """
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result, (time.time() - start_time) * 1000
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Edge-Cloud roundtrip latency for failed {func.__name__}: {latency_ms:.2f} ms"
            )
            raise e
