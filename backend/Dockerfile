# Multi-stage build untuk optimasi ukuran image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies untuk MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies dari builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create uploads directory structure
RUN mkdir -p uploads/evidence/installed/2025 \
    uploads/evidence/return/2025 \
    uploads/evidence/stock_in/2025 \
    uploads/evidence/stock_out/2025

# Make sure scripts are executable
RUN chmod +x run.py 2>/dev/null || true

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

