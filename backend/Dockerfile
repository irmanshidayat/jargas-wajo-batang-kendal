# Multi-stage build untuk optimasi ukuran image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Konfigurasi apt untuk handle network issues dan unavailable repositories
RUN echo 'Acquire::http::Timeout "30";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "30";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Install system dependencies dengan retry mechanism dan timeout
# Menggunakan retry untuk handle network issues dan timeout untuk menghindari stuck
RUN for i in 1 2 3; do \
        timeout 120 apt-get update -o Acquire::http::Timeout=30 -o Acquire::ftp::Timeout=30 && \
        timeout 300 apt-get install -y --no-install-recommends \
            gcc \
            default-libmysqlclient-dev \
            pkg-config && \
        rm -rf /var/lib/apt/lists/* && break || \
        (echo "Install attempt $i failed, retrying..." && sleep 5 && rm -rf /var/lib/apt/lists/*); \
    done

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Konfigurasi apt untuk handle network issues dan unavailable repositories
RUN echo 'Acquire::http::Timeout "30";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "30";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Install runtime dependencies untuk MySQL dengan retry mechanism dan timeout
RUN for i in 1 2 3; do \
        timeout 120 apt-get update -o Acquire::http::Timeout=30 -o Acquire::ftp::Timeout=30 && \
        timeout 300 apt-get install -y --no-install-recommends \
            default-libmysqlclient-dev && \
        rm -rf /var/lib/apt/lists/* && break || \
        (echo "Install attempt $i failed, retrying..." && sleep 5 && rm -rf /var/lib/apt/lists/*); \
    done

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

