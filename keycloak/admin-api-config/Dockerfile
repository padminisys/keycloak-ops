# Padmini Systems Keycloak Configuration
# Simple Docker build for Python Keycloak configuration
FROM python:3.13-slim

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Add metadata
LABEL maintainer="Padmini Systems <devops@padmini.systems>"
LABEL org.opencontainers.image.title="Keycloak Python Configuration"
LABEL org.opencontainers.image.description="Enterprise-grade Keycloak configuration using Python Admin API"
LABEL org.opencontainers.image.version=${VERSION}
LABEL org.opencontainers.image.created=${BUILD_DATE}
LABEL org.opencontainers.image.revision=${VCS_REF}
LABEL org.opencontainers.image.source="https://github.com/padminisys/keycloak-ops"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r padmini && useradd -r -g padmini -s /bin/false -d /app padmini

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY python-executor/requirements.txt .

# Install Python dependencies globally (not with --user)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Copy Python application
COPY python-executor/ ./

# Set ownership and permissions
RUN chown -R padmini:padmini /app && \
    chmod -R 755 /app && \
    chmod +x main.py

# Switch to non-root user
USER padmini

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default action
ENV ACTION=create

# Entry point
ENTRYPOINT ["python", "main.py"]

# Default command
CMD []
