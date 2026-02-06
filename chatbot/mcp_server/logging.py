# Task T007: Structured Logging
"""Structured JSON logging configuration using structlog.

Provides structured logging for MCP tool calls with:
- Tool name, user_id, latency_ms, status
- Correlation IDs for error tracing
- JSON output to stdout

References:
- spec.md: FR-065-067 (observability requirements)
- plan.md: Structured logging decision
"""

import logging
import sys
import time
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable
from uuid import UUID, uuid4

import structlog

from mcp_server.config import get_settings

settings = get_settings()

# Context variable for correlation ID (request-scoped)
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    cid = correlation_id_var.get()
    if not cid:
        cid = str(uuid4())[:8]
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(cid)


def add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Structlog processor to add correlation ID."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def configure_logging() -> None:
    """Configure structlog for JSON output.

    Call this once at application startup.
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_correlation_id,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "mcp_server") -> structlog.BoundLogger:
    """Get a structlog logger instance.

    Args:
        name: Logger name (default: mcp_server)

    Returns:
        Configured structlog BoundLogger
    """
    return structlog.get_logger(name)


def log_tool_call(
    tool_name: str,
    user_id: UUID | str,
    success: bool,
    latency_ms: float,
    error: str | None = None,
    **extra: Any,
) -> None:
    """Log an MCP tool invocation.

    Per FR-066: Log tool name, user_id, latency (ms), and success/error status.

    Args:
        tool_name: Name of the MCP tool invoked
        user_id: User ID for the request
        success: Whether the call succeeded
        latency_ms: Request latency in milliseconds
        error: Error message if failed
        **extra: Additional context to log
    """
    logger = get_logger("mcp_tools")

    log_data = {
        "tool_name": tool_name,
        "user_id": str(user_id),
        "latency_ms": round(latency_ms, 2),
        "status": "success" if success else "error",
        **extra,
    }

    if error:
        log_data["error"] = error
        logger.error("tool_call_failed", **log_data)
    else:
        logger.info("tool_call_completed", **log_data)


def with_tool_logging(tool_name: str) -> Callable:
    """Decorator to automatically log tool calls.

    Usage:
        @with_tool_logging("add_task")
        async def add_task(user_id: UUID, title: str) -> dict:
            ...

    Args:
        tool_name: Name of the tool for logging

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            user_id = kwargs.get("user_id", "unknown")

            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.perf_counter() - start_time) * 1000
                log_tool_call(tool_name, user_id, success=True, latency_ms=latency_ms)
                return result
            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000
                log_tool_call(
                    tool_name, user_id, success=False, latency_ms=latency_ms, error=str(e)
                )
                raise

        return wrapper

    return decorator
