# ============================
# 1. BUILDER STAGE
# ============================
FROM python:3.11-slim as builder

# Create working directory inside the container
WORKDIR /app
RUN echo "--- BUILDING BACKEND-ONLY VERSION ---"

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies file
COPY requirements.txt .

# Suppress pip root warning
ENV PIP_ROOT_USER_ACTION=ignore

# Install Python dependencies into a temporary directory
# We use --prefix=/install so we can easily copy them to /usr/local in the next stage
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


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

# Copy installed dependencies from the builder stage to /usr/local
# making them available to all users (including appuser) and puts them in PATH
COPY --from=builder /install /usr/local
ENV PATH="/usr/local/bin:$PATH"

# Copy application source code
COPY server.py .
COPY auth.py .
COPY database.py .
COPY geo_helper.py .
COPY order ./order
COPY payment ./payment
COPY community ./community
COPY messaging ./messaging

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

# Expose the application port
EXPOSE ${PORT}

<<<<<<< HEAD
# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
=======
# Start the application using Uvicorn
CMD sh -c "uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 4"
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49
