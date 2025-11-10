# 🚀 Setup Nginx Host - Instruksi Cepat

## Cara 1: Copy-Paste Perintah (Recommended)

Jalankan perintah berikut di server SSH Anda:

```bash
# 1. Masuk ke direktori project
cd ~/jargas-wajo-batang-kendal

# 2. Copy konfigurasi
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas

# 3. Buat symbolic link
sudo ln -sf /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas

# 4. Hapus default config (opsional)
sudo rm -f /etc/nginx/sites-enabled/default

# 5. Test konfigurasi
sudo nginx -t

# 6. Reload nginx
sudo systemctl reload nginx

# 7. Verifikasi
sudo systemctl status nginx
curl http://localhost/health
```

## Cara 2: Menggunakan Script

```bash
# Di server SSH
cd ~/jargas-wajo-batang-kendal
bash nginx-host/setup-instructions.sh
```

## Verifikasi Setup

Setelah setup, test dengan:

```bash
# Test health check
curl http://localhost/health

# Test frontend (harus return HTML)
curl http://localhost/

# Test backend API
curl http://localhost/api/v1/health

# Check nginx status
sudo systemctl status nginx

# Check nginx config
sudo nginx -t
```

## Edit Domain (Jika Ada)

```bash
sudo nano /etc/nginx/sites-available/jargas
```

Ubah baris:
```nginx
server_name _;  # Ganti ini
```

Menjadi:
```nginx
server_name your-domain.com www.your-domain.com;
```

Lalu reload:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## Setup SSL/TLS (Let's Encrypt)

```bash
# Install certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Dapatkan SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Troubleshooting

### Nginx tidak start
```bash
# Check error
sudo nginx -t
sudo journalctl -u nginx -n 50
```

### Port 80 sudah digunakan
```bash
# Check apa yang menggunakan port 80
sudo netstat -tulpn | grep :80
sudo lsof -i :80
```

### Container tidak bisa diakses
```bash
# Check container status
docker-compose ps

# Check port mapping
docker-compose port frontend 80
docker-compose port backend 8000

# Test dari dalam container
docker exec jargas_frontend wget -qO- http://127.0.0.1/
```

## Rebuild Container (Setelah Fix Healthcheck)

```bash
# Rebuild frontend container
docker-compose build frontend

# Restart dengan rebuild
docker-compose up -d --build frontend

# Check health status
docker-compose ps
```

