# ============================================================================
# Multi-stage Dockerfile for Script Analysis System
# ============================================================================
# This Dockerfile creates an optimized production image for the screenplay
# narrative structure analysis system with Web UI support.
# ============================================================================

# ============================================================================
# Stage 1: Base Python Image
# ============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 2: Builder (Install Dependencies)
# ============================================================================
FROM base AS builder

WORKDIR /tmp

# Copy requirements files
COPY requirements.txt requirements-web.txt ./

# Install Python dependencies
RUN pip install --user --no-warn-script-location \
    -r requirements.txt \
    -r requirements-web.txt

# ============================================================================
# Stage 3: Runtime Image
# ============================================================================
FROM base AS runtime

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /data && \
    chown -R appuser:appuser /app /data

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Set PATH to include user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Create necessary directories
RUN mkdir -p \
    /app/uploads \
    /app/outputs \
    /app/ab_tests \
    /app/parse_jobs \
    /data/uploads \
    /data/outputs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Start web server
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Build Instructions:
# ============================================================================
# Build image:
#   docker build -t screenplay-analysis:latest .
#
# Run container:
#   docker run -d -p 8000:8000 \
#     -v $(pwd)/.env:/app/.env:ro \
#     -v screenplay-data:/data \
#     --name screenplay-web \
#     screenplay-analysis:latest
#
# View logs:
#   docker logs -f screenplay-web
#
# Stop container:
#   docker stop screenplay-web
# ============================================================================
