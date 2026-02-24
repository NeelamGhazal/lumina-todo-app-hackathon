# Task T033: Dockerfile for MCP Server
# Multi-stage build for Python 3.13 with UV

# Stage 1: Build
FROM python:3.13-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .
COPY mcp_server/ mcp_server/
COPY agent/ agent/

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/mcp_server /app/mcp_server
COPY --from=builder /app/agent /app/agent

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default environment
ENV MCP_SERVER_PORT=8001
ENV MCP_SERVER_HOST=0.0.0.0
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run the application
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8001"]
