# 🚀 Setup Nginx untuk Backend Jargas APBN

Konfigurasi Nginx untuk reverse proxy ke backend FastAPI yang berjalan tanpa Docker.

## 📋 Prasyarat

1. **Nginx sudah terinstall**
   - Linux: `sudo apt install nginx` (Ubuntu/Debian) atau `sudo yum install nginx` (CentOS/RHEL)
   - Windows: Download dari https://nginx.org/en/download.html

2. **Backend sudah berjalan**
   - Production: `localhost:8010`
   - Development: `localhost:8020`

## 🔧 Setup di Linux (VPS/Server)

### 1. Copy Konfigurasi

**Production:**
```bash
sudo cp backend/nginx/nginx.conf.production /etc/nginx/sites-available/jargas-backend
```

**Development:**
```bash
sudo cp backend/nginx/nginx.conf.development /etc/nginx/sites-available/jargas-backend-dev
```

### 2. Aktifkan Konfigurasi

**Production:**
```bash
sudo ln -s /etc/nginx/sites-available/jargas-backend /etc/nginx/sites-enabled/
```

**Development:**
```bash
sudo ln -s /etc/nginx/sites-available/jargas-backend-dev /etc/nginx/sites-enabled/
```

### 3. Test Konfigurasi

```bash
sudo nginx -t
```

Jika berhasil, akan muncul:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4. Reload Nginx

```bash
sudo systemctl reload nginx
```

Atau restart:
```bash
sudo systemctl restart nginx
```

### 5. Verifikasi

**Cek status:**
```bash
sudo systemctl status nginx
```

**Test backend melalui nginx:**
```bash
# Production
curl http://jargas.ptkiansantang.com/health
curl http://jargas.ptkiansantang.com/api/v1/

# Development
curl http://devjargas.ptkiansantang.com/health
curl http://devjargas.ptkiansantang.com/api/v1/
```

## 🪟 Setup di Windows (Development Lokal)

### 1. Install Nginx

1. Download dari https://nginx.org/en/download.html
2. Extract ke folder (contoh: `C:\nginx`)
3. Jalankan `nginx.exe` dari folder tersebut

### 2. Copy Konfigurasi

**Production:**
```powershell
# Buat folder sites-available jika belum ada
New-Item -ItemType Directory -Force -Path "C:\nginx\conf\sites-available"
Copy-Item "backend\nginx\nginx.conf.production" "C:\nginx\conf\sites-available\jargas-backend.conf"
```

**Development:**
```powershell
Copy-Item "backend\nginx\nginx.conf.development" "C:\nginx\conf\sites-available\jargas-backend-dev.conf"
```

### 3. Edit nginx.conf Utama

Edit file `C:\nginx\conf\nginx.conf`, tambahkan di dalam block `http {}`:

```nginx
http {
    # ... konfigurasi lainnya ...
    
    # Include konfigurasi backend
    include sites-available/jargas-backend.conf;
    # include sites-available/jargas-backend-dev.conf;  # Uncomment untuk dev
}
```

### 4. Test dan Reload

```powershell
# Test konfigurasi
cd C:\nginx
.\nginx.exe -t

# Reload nginx
.\nginx.exe -s reload
```

### 5. Verifikasi

```powershell
# Test di browser atau PowerShell
Invoke-WebRequest -Uri "http://localhost/health"
Invoke-WebRequest -Uri "http://localhost/api/v1/"
```

## 🔒 Setup SSL/TLS (Let's Encrypt)

### 1. Install Certbot

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### 2. Generate Certificate

**Production:**
```bash
sudo certbot --nginx -d jargas.ptkiansantang.com
```

**Development:**
```bash
sudo certbot --nginx -d devjargas.ptkiansantang.com
```

### 3. Aktifkan HTTPS di Konfigurasi

Edit file konfigurasi nginx:
1. Uncomment block `server` untuk HTTPS (port 443)
2. Uncomment block redirect HTTP ke HTTPS (port 80)
3. Sesuaikan path SSL certificate jika berbeda

### 4. Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Auto-renewal

Certbot sudah setup auto-renewal. Verifikasi:

```bash
sudo certbot renew --dry-run
```

## 📝 Konfigurasi Port

Pastikan port backend sesuai dengan konfigurasi:

- **Production**: Port `8010` (sesuai `backend/.env` atau `backend/env.prod.example`)
- **Development**: Port `8020` (sesuai `backend/.env.dev` atau `backend/env.dev.example`)

Jika port berbeda, edit file konfigurasi nginx:
- Cari `upstream backend_jargas` atau `upstream backend_jargas_dev`
- Ubah `server 127.0.0.1:8010;` atau `server 127.0.0.1:8020;` sesuai port backend

## 🔍 Troubleshooting

### Nginx tidak start

```bash
# Cek error log
sudo tail -f /var/log/nginx/error.log

# Cek syntax
sudo nginx -t
```

### Backend tidak bisa diakses

1. **Cek backend berjalan:**
   ```bash
   # Production
   curl http://localhost:8010/health
   
   # Development
   curl http://localhost:8020/health
   ```

2. **Cek port tidak bentrok:**
   ```bash
   sudo netstat -tulpn | grep :8010
   sudo netstat -tulpn | grep :8020
   ```

3. **Cek firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

### 502 Bad Gateway

- Backend tidak berjalan atau port salah
- Cek log nginx: `sudo tail -f /var/log/nginx/jargas-backend-error.log`
- Cek backend log untuk error detail

### 404 Not Found

- Pastikan path `/api` sudah benar di konfigurasi
- Cek `proxy_pass` di konfigurasi nginx
- Pastikan backend route sudah benar

## 📊 Monitoring

### Cek Log Access

```bash
# Production
sudo tail -f /var/log/nginx/jargas-backend-access.log

# Development
sudo tail -f /var/log/nginx/jargas-backend-dev-access.log
```

### Cek Log Error

```bash
# Production
sudo tail -f /var/log/nginx/jargas-backend-error.log

# Development
sudo tail -f /var/log/nginx/jargas-backend-dev-error.log
```

## 🔄 Reload/Restart Nginx

```bash
# Test dulu
sudo nginx -t

# Reload (graceful, tidak drop connection)
sudo systemctl reload nginx

# Atau restart (hard restart)
sudo systemctl restart nginx
```

## 📚 Referensi

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Let's Encrypt](https://letsencrypt.org/)

