import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LatencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logging.info(
            f"Path: {request.url.path} | Latency: {process_time:.4f}s | Method: {request.method}"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response
