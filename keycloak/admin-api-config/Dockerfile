# Padmini Systems Keycloak Configuration
# Multi-stage secure Docker build
FROM python:3.13-slim as builder

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

# Create non-root user for security
RUN groupadd -r padmini && useradd -r -g padmini -s /bin/false padmini

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY python-executor/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# Copy Python application
COPY python-executor/ ./app/

# Validate Python syntax
RUN python -m py_compile app/main.py && \
    python -m py_compile app/config/environment.py && \
    python -m py_compile app/config/constants.py && \
    python -m py_compile app/utils/logger.py && \
    python -m py_compile app/utils/keycloak_client.py

#############################################
# Production stage
#############################################
FROM python:3.13-slim as production

# Set build arguments for production
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

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r padmini && useradd -r -g padmini -s /bin/false -d /app padmini

# Set working directory
WORKDIR /app

# Copy application code from builder
COPY --from=builder /build/app/ ./

# Copy requirements and install Python packages in production
COPY python-executor/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt && \
    rm requirements.txt

# Set ownership and permissions
RUN chown -R padmini:padmini /app /home/padmini && \
    chmod -R 755 /app && \
    chmod +x main.py

# Switch to non-root user
USER padmini

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/padmini/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default action
ENV ACTION=create

# Entry point
ENTRYPOINT ["python", "main.py"]

# Default command
CMD []
