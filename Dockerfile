# ============================
# 1. BUILDER STAGE
# ============================
FROM python:3.11-slim as builder

# Create working directory inside the container
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies file
COPY backend/requirements.txt .

# Install Python dependencies into local user directory
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir --user -r requirements.txt


# ============================
# 2. PRODUCTION STAGE
# ============================
FROM python:3.11-slim

# Working directory for the application
WORKDIR /app

# Install lightweight runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application source code
COPY backend/ .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8001

# Expose the application port
EXPOSE ${PORT}

# Add health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", 8001)}/api/health', timeout=5)" || exit 1

# Start the application using Uvicorn
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 4"]
