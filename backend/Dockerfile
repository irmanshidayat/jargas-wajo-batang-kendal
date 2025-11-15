# Multi-stage build untuk optimasi ukuran image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Konfigurasi apt untuk handle network issues dan unavailable repositories
RUN echo 'Acquire::http::Timeout "60";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "60";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "5";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'APT::Get::AllowUnauthenticated "false";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Check-Valid-Until "false";' >> /etc/apt/apt.conf.d/99timeout

# Install system dependencies dengan retry mechanism dan timeout
# Menggunakan retry untuk handle network issues dan timeout untuk menghindari stuck
# Menambahkan opsi untuk skip unavailable repositories dan menggunakan mirror alternatif
RUN for i in 1 2 3 4 5; do \
        echo "=== Attempt $i: Updating package lists ==="; \
        timeout 180 apt-get update \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false \
            -o APT::Get::Allow-Redirect=false \
            -o Debug::pkgProblemResolver=0 \
            -o Debug::NoLocking=1 2>&1 | (grep -v "^Ign:" || true) && \
        echo "=== Attempt $i: Installing packages ===" && \
        timeout 600 apt-get install -y --no-install-recommends \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false \
            gcc \
            default-libmysqlclient-dev \
            pkg-config && \
        echo "=== Packages installed successfully ===" && \
        rm -rf /var/lib/apt/lists/* && break || \
        (echo "=== Install attempt $i failed, retrying in 15 seconds... ===" && \
         rm -rf /var/lib/apt/lists/* && \
         [ $i -lt 5 ] && sleep 15 || (echo "=== All retry attempts failed ===" && exit 1)); \
    done

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Konfigurasi apt untuk handle network issues dan unavailable repositories
RUN echo 'Acquire::http::Timeout "60";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "60";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "5";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'APT::Get::AllowUnauthenticated "false";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Check-Valid-Until "false";' >> /etc/apt/apt.conf.d/99timeout

# Install runtime dependencies untuk MySQL dengan retry mechanism dan timeout
# Menambahkan opsi untuk skip unavailable repositories dan menggunakan mirror alternatif
RUN for i in 1 2 3 4 5; do \
        echo "=== Attempt $i: Updating package lists ==="; \
        timeout 180 apt-get update \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false \
            -o APT::Get::Allow-Redirect=false \
            -o Debug::pkgProblemResolver=0 \
            -o Debug::NoLocking=1 2>&1 | (grep -v "^Ign:" || true) && \
        echo "=== Attempt $i: Installing packages ===" && \
        timeout 600 apt-get install -y --no-install-recommends \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false \
            default-libmysqlclient-dev && \
        echo "=== Packages installed successfully ===" && \
        rm -rf /var/lib/apt/lists/* && break || \
        (echo "=== Install attempt $i failed, retrying in 15 seconds... ===" && \
         rm -rf /var/lib/apt/lists/* && \
         [ $i -lt 5 ] && sleep 15 || (echo "=== All retry attempts failed ===" && exit 1)); \
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

