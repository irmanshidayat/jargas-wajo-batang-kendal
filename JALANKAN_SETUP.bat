@echo off
REM Script untuk Setup Nginx Host dari Windows
REM Pastikan Anda sudah punya akses SSH ke server

echo ==========================================
echo Setup Nginx Host untuk Jargas APBN
echo ==========================================
echo.

set /p SERVER_IP="Masukkan IP Server: "
set /p USERNAME="Masukkan Username SSH: "
set /p PROJECT_PATH="Masukkan path project di server (default: ~/jargas-wajo-batang-kendal): "

if "%PROJECT_PATH%"=="" set PROJECT_PATH=~/jargas-wajo-batang-kendal

echo.
echo Konfigurasi:
echo   Server: %USERNAME%@%SERVER_IP%
echo   Path: %PROJECT_PATH%
echo.
echo Menjalankan setup...
echo.

ssh %USERNAME%@%SERVER_IP% "cd %PROJECT_PATH% && \
if [ ! -f nginx-host/jargas.conf ]; then \
    echo '❌ File konfigurasi tidak ditemukan!'; \
    exit 1; \
fi && \
echo '📝 Copy konfigurasi...' && \
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas && \
echo '🔗 Buat symbolic link...' && \
sudo ln -sf /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas && \
echo '📦 Hapus default config...' && \
sudo rm -f /etc/nginx/sites-enabled/default && \
echo '🧪 Test konfigurasi nginx...' && \
sudo nginx -t && \
echo '🔄 Reload nginx...' && \
sudo systemctl reload nginx && \
echo '' && \
echo '✅ Setup selesai!' && \
echo '' && \
echo '📊 Status nginx:' && \
sudo systemctl status nginx --no-pager -l | head -5 && \
echo '' && \
echo '🏥 Test health check:' && \
curl -s http://localhost/health || echo '⚠️  Health check gagal (container mungkin belum ready)'"

echo.
echo ==========================================
echo Setup Selesai!
echo ==========================================
echo.
echo Langkah selanjutnya:
echo 1. Rebuild container: ssh %USERNAME%@%SERVER_IP% "cd %PROJECT_PATH% && docker-compose build frontend && docker-compose up -d frontend"
echo 2. Test: ssh %USERNAME%@%SERVER_IP% "curl http://localhost/health"
echo.
pause

