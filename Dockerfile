# Q-BIT: Advanced Omni Agent & Swarm Intelligence Hub
# Multi-stage Docker build for production deployment

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY README.md LICENSE ./

# Install the package
RUN pip install -e .

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    QBIT_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r qbit && useradd -r -g qbit qbit

# Create app directory
WORKDIR /app

# Copy from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app ./

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R qbit:qbit /app

# Switch to non-root user
USER qbit

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 8001 8002

# Default command
CMD ["python", "-m", "src.main", "start"]

# Development stage
FROM builder as development

# Install development dependencies
RUN pip install -e ".[dev]"

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Set development environment
ENV QBIT_ENV=development

# Default command for development
CMD ["python", "-m", "src.main", "start", "--strategy", "adaptive"]
