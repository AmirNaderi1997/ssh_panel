import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.app.core.logging import logger


class RequestLogMiddleware(BaseHTTPMiddleware):
    """Middleware for adding Correlation ID and logging all requests/responses."""
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate a unique correlation ID for tracking
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        # Record start time
        start_time = time.time()

        # Log request receipt
        logger.info(
            "Request received",
            path=request.url.path,
            method=request.method,
            client_host=request.client.host if request.client else None,
            correlation_id=correlation_id,
        )

        try:
            response = await call_next(request)
        except Exception as e:
            # Log failure
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                path=request.url.path,
                method=request.method,
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                correlation_id=correlation_id,
            )
            raise e

        # Calculate duration
        duration = time.time() - start_time
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(duration)

        # Log response
        logger.info(
            "Request completed",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            correlation_id=correlation_id,
        )

        return response
