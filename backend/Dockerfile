# Multi-stage build untuk optimasi ukuran image
FROM ubuntu:24.04 as builder

# Set working directory
WORKDIR /app

# Set environment variables untuk non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Konfigurasi apt untuk handle network issues dan unavailable repositories
RUN echo 'Acquire::http::Timeout "60";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "60";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "5";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'APT::Get::AllowUnauthenticated "false";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Check-Valid-Until "false";' >> /etc/apt/apt.conf.d/99timeout

# Pastikan repository sources terkonfigurasi dengan benar untuk Ubuntu 24.04
RUN if [ ! -f /etc/apt/sources.list ] || [ ! -s /etc/apt/sources.list ] || ! grep -q "archive.ubuntu.com\|mirror.ubuntu.com" /etc/apt/sources.list 2>/dev/null; then \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse" > /etc/apt/sources.list && \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse" >> /etc/apt/sources.list && \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble-backports main restricted universe multiverse" >> /etc/apt/sources.list; \
    fi && \
    echo "=== Repository sources configured ===" && \
    cat /etc/apt/sources.list || true

# Install Python 3.11 dan system dependencies dengan retry mechanism
# Ubuntu 24.04 default Python 3.12, jadi perlu install Python 3.11 dari deadsnakes PPA
RUN for i in 1 2 3 4 5; do \
        echo "=== Attempt $i: Updating package lists ==="; \
        if timeout 180 apt-get update \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false; then \
            echo "=== Package lists updated successfully ==="; \
            echo "=== Attempt $i: Installing packages ==="; \
            if timeout 600 apt-get install -y --no-install-recommends \
                -o Acquire::http::Timeout=60 \
                -o Acquire::ftp::Timeout=60 \
                -o Acquire::Check-Valid-Until=false \
                -o APT::Get::AllowUnauthenticated=false \
                software-properties-common \
                ca-certificates \
                curl; then \
                echo "=== Basic packages installed ==="; \
                add-apt-repository -y ppa:deadsnakes/ppa && \
                apt-get update -o Acquire::http::Timeout=60 -o Acquire::ftp::Timeout=60; \
            fi && \
            if timeout 600 apt-get install -y --no-install-recommends \
                -o Acquire::http::Timeout=60 \
                -o Acquire::ftp::Timeout=60 \
                -o Acquire::Check-Valid-Until=false \
                -o APT::Get::AllowUnauthenticated=false \
                python3.11 \
                python3.11-dev \
                python3.11-distutils \
                gcc \
                libmysqlclient-dev \
                pkg-config; then \
                echo "=== Packages installed successfully ==="; \
                rm -rf /var/lib/apt/lists/*; \
                break; \
            else \
                echo "=== Package installation failed ==="; \
                echo "=== Searching for available packages ==="; \
                apt-cache search python3.11 2>&1 | head -5 || true; \
                apt-cache search mysqlclient 2>&1 | head -5 || true; \
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

# Install pip untuk Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    python3.11 -m pip install --upgrade pip setuptools wheel

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM ubuntu:24.04

# Set working directory
WORKDIR /app

# Set environment variables untuk non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Konfigurasi apt untuk handle network issues dan unavailable repositories
RUN echo 'Acquire::http::Timeout "60";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "60";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "5";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'APT::Get::AllowUnauthenticated "false";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Check-Valid-Until "false";' >> /etc/apt/apt.conf.d/99timeout

# Pastikan repository sources terkonfigurasi dengan benar untuk Ubuntu 24.04
RUN if [ ! -f /etc/apt/sources.list ] || [ ! -s /etc/apt/sources.list ] || ! grep -q "archive.ubuntu.com\|mirror.ubuntu.com" /etc/apt/sources.list 2>/dev/null; then \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse" > /etc/apt/sources.list && \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse" >> /etc/apt/sources.list && \
        echo "deb http://archive.ubuntu.com/ubuntu/ noble-backports main restricted universe multiverse" >> /etc/apt/sources.list; \
    fi && \
    echo "=== Repository sources configured ===" && \
    cat /etc/apt/sources.list || true

# Install Python 3.11 dan runtime dependencies untuk MySQL dengan retry mechanism
RUN for i in 1 2 3 4 5; do \
        echo "=== Attempt $i: Updating package lists ==="; \
        if timeout 180 apt-get update \
            -o Acquire::http::Timeout=60 \
            -o Acquire::ftp::Timeout=60 \
            -o Acquire::Check-Valid-Until=false \
            -o APT::Get::AllowUnauthenticated=false; then \
            echo "=== Package lists updated successfully ==="; \
            echo "=== Attempt $i: Installing packages ==="; \
            if timeout 600 apt-get install -y --no-install-recommends \
                -o Acquire::http::Timeout=60 \
                -o Acquire::ftp::Timeout=60 \
                -o Acquire::Check-Valid-Until=false \
                -o APT::Get::AllowUnauthenticated=false \
                software-properties-common \
                ca-certificates \
                curl; then \
                echo "=== Basic packages installed ==="; \
                add-apt-repository -y ppa:deadsnakes/ppa && \
                apt-get update -o Acquire::http::Timeout=60 -o Acquire::ftp::Timeout=60; \
            fi && \
            if timeout 600 apt-get install -y --no-install-recommends \
                -o Acquire::http::Timeout=60 \
                -o Acquire::ftp::Timeout=60 \
                -o Acquire::Check-Valid-Until=false \
                -o APT::Get::AllowUnauthenticated=false \
                python3.11 \
                python3.11-dev \
                python3.11-distutils \
                libmysqlclient-dev; then \
                echo "=== Packages installed successfully ==="; \
                rm -rf /var/lib/apt/lists/*; \
                break; \
            else \
                echo "=== Package installation failed ==="; \
                echo "=== Searching for available packages ==="; \
                apt-cache search python3.11 2>&1 | head -5 || true; \
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

# Install pip untuk Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    python3.11 -m pip install --upgrade pip setuptools wheel

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
    CMD python3.11 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["python3.11", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

