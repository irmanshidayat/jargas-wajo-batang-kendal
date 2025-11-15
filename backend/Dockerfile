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

# Pastikan repository sources terkonfigurasi dengan benar
# Deteksi versi Debian dan konfigurasi repository sesuai
RUN DEBIAN_VERSION=$(cat /etc/os-release | grep VERSION_CODENAME | cut -d= -f2 || echo "bookworm") && \
    if [ ! -f /etc/apt/sources.list ] || [ ! -s /etc/apt/sources.list ] || ! grep -q "deb.debian.org" /etc/apt/sources.list 2>/dev/null; then \
        echo "deb http://deb.debian.org/debian ${DEBIAN_VERSION} main" > /etc/apt/sources.list && \
        echo "deb http://deb.debian.org/debian ${DEBIAN_VERSION}-updates main" >> /etc/apt/sources.list && \
        echo "deb http://security.debian.org/debian-security ${DEBIAN_VERSION}-security main" >> /etc/apt/sources.list; \
    fi && \
    echo "=== Repository sources configured ===" && \
    cat /etc/apt/sources.list || true

# Install system dependencies dengan retry mechanism dan timeout
# Menggunakan retry untuk handle network issues dan timeout untuk menghindari stuck
RUN for i in 1 2 3 4 5; do \
        echo "=== Attempt $i: Updating package lists ==="; \
        if timeout 180 apt-get update \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false; then \
            echo "=== Package lists updated successfully ==="; \
            echo "=== Attempt $i: Installing packages ==="; \
            MYSQL_DEV_PKG="default-libmysqlclient-dev" && \
            if ! apt-cache show ${MYSQL_DEV_PKG} >/dev/null 2>&1; then \
                echo "=== Trying alternative package name: libmysqlclient-dev ==="; \
                MYSQL_DEV_PKG="libmysqlclient-dev"; \
            fi && \
            if timeout 600 apt-get install -y --no-install-recommends \
                -o Acquire::http::Timeout=60 \
                -o Acquire::ftp::Timeout=60 \
                -o Acquire::Check-Valid-Until=false \
                -o APT::Get::AllowUnauthenticated=false \
                gcc \
                ${MYSQL_DEV_PKG} \
                pkg-config; then \
                echo "=== Packages installed successfully ==="; \
                rm -rf /var/lib/apt/lists/*; \
                break; \
            else \
                echo "=== Package installation failed ==="; \
                echo "=== Searching for available packages ==="; \
                apt-cache search gcc 2>&1 | head -5 || true; \
                apt-cache search mysqlclient 2>&1 | head -5 || true; \
                apt-cache search pkg-config 2>&1 | head -5 || true; \
            fi; \
        else \
            echo "=== Package list update failed ==="; \
        fi; \
        if [ $i -lt 5 ]; then \
            echo "=== Retrying in 15 seconds... ==="; \
            rm -rf /var/lib/apt/lists/*; \
            sleep 15; \
        else \
            echo "=== All retry attempts failed ==="; \
            exit 1; \
        fi; \
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

# Pastikan repository sources terkonfigurasi dengan benar
# Deteksi versi Debian dan konfigurasi repository sesuai
RUN DEBIAN_VERSION=$(cat /etc/os-release | grep VERSION_CODENAME | cut -d= -f2 || echo "bookworm") && \
    if [ ! -f /etc/apt/sources.list ] || [ ! -s /etc/apt/sources.list ] || ! grep -q "deb.debian.org" /etc/apt/sources.list 2>/dev/null; then \
        echo "deb http://deb.debian.org/debian ${DEBIAN_VERSION} main" > /etc/apt/sources.list && \
        echo "deb http://deb.debian.org/debian ${DEBIAN_VERSION}-updates main" >> /etc/apt/sources.list && \
        echo "deb http://security.debian.org/debian-security ${DEBIAN_VERSION}-security main" >> /etc/apt/sources.list; \
    fi && \
    echo "=== Repository sources configured ===" && \
    cat /etc/apt/sources.list || true

# Install runtime dependencies untuk MySQL dengan retry mechanism dan timeout
RUN for i in 1 2 3 4 5; do \
        echo "=== Attempt $i: Updating package lists ==="; \
        if timeout 180 apt-get update \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false; then \
            echo "=== Package lists updated successfully ==="; \
            echo "=== Attempt $i: Installing packages ==="; \
            MYSQL_DEV_PKG="default-libmysqlclient-dev" && \
            if ! apt-cache show ${MYSQL_DEV_PKG} >/dev/null 2>&1; then \
                echo "=== Trying alternative package name: libmysqlclient-dev ==="; \
                MYSQL_DEV_PKG="libmysqlclient-dev"; \
            fi && \
            if timeout 600 apt-get install -y --no-install-recommends \
                -o Acquire::http::Timeout=60 \
                -o Acquire::ftp::Timeout=60 \
                -o Acquire::Check-Valid-Until=false \
                -o APT::Get::AllowUnauthenticated=false \
                ${MYSQL_DEV_PKG}; then \
                echo "=== Packages installed successfully ==="; \
                rm -rf /var/lib/apt/lists/*; \
                break; \
            else \
                echo "=== Package installation failed ==="; \
                echo "=== Searching for available packages ==="; \
                apt-cache search mysqlclient 2>&1 | head -10 || true; \
            fi; \
        else \
            echo "=== Package list update failed ==="; \
        fi; \
        if [ $i -lt 5 ]; then \
            echo "=== Retrying in 15 seconds... ==="; \
            rm -rf /var/lib/apt/lists/*; \
            sleep 15; \
        else \
            echo "=== All retry attempts failed ==="; \
            exit 1; \
        fi; \
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

