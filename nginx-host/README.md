# Setup Nginx Host untuk Production

## Best Practice Architecture

```
Internet → Nginx Host (Port 80/443) → Container Frontend (Port 8080) → Container Backend (Port 8001)
```

### Keuntungan Setup Ini:

1. **SSL/TLS Termination** di nginx host (lebih efisien)
2. **Rate Limiting** untuk proteksi DDoS
3. **Security Headers** terpusat
4. **Load Balancing** mudah ditambahkan
5. **Monitoring** lebih mudah (log terpusat)
6. **Container tetap terisolasi** dan portable

## Instalasi

### 1. Copy konfigurasi nginx

```bash
# Copy file konfigurasi
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas

# Buat symbolic link
sudo ln -s /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/

# Hapus default nginx config (opsional)
sudo rm /etc/nginx/sites-enabled/default
```

### 2. Edit konfigurasi sesuai domain Anda

```bash
sudo nano /etc/nginx/sites-available/jargas
```

Ubah `server_name _;` menjadi domain Anda:
```nginx
server_name your-domain.com www.your-domain.com;
```

### 3. Test konfigurasi nginx

```bash
sudo nginx -t
```

### 4. Reload nginx

```bash
sudo systemctl reload nginx
```

### 5. Verifikasi

```bash
# Cek status nginx
sudo systemctl status nginx

# Test akses
curl http://localhost/health
```

## Setup SSL/TLS (Let's Encrypt)

### 1. Install Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Dapatkan SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Auto-renewal (sudah otomatis)

Certbot akan setup auto-renewal. Test dengan:
```bash
sudo certbot renew --dry-run
```

### 4. Uncomment HTTPS section di jargas.conf

Setelah SSL terpasang, uncomment bagian HTTPS di `/etc/nginx/sites-available/jargas` dan update path SSL certificate.

## Monitoring

### Log Files

```bash
# Access log
sudo tail -f /var/log/nginx/jargas_access.log

# Error log
sudo tail -f /var/log/nginx/jargas_error.log
```

### Status Check

```bash
# Nginx status
sudo systemctl status nginx

# Container status
docker-compose ps
```

## Troubleshooting

### Nginx tidak start

```bash
# Check error
sudo nginx -t
sudo journalctl -u nginx -n 50

# Check port conflict
sudo netstat -tulpn | grep :80
```

### Container tidak bisa diakses

```bash
# Check container running
docker-compose ps

# Check port mapping
docker-compose port frontend 80
docker-compose port backend 8000
```

### Rate limiting terlalu ketat

Edit `/etc/nginx/sites-available/jargas` dan sesuaikan:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

## Security Best Practices

1. ✅ **Firewall aktif** (UFW sudah dikonfigurasi)
2. ✅ **Rate limiting** (sudah dikonfigurasi)
3. ✅ **Security headers** (sudah dikonfigurasi)
4. ✅ **SSL/TLS** (setup setelah domain ready)
5. ✅ **Regular updates** (`sudo apt update && sudo apt upgrade`)
6. ✅ **Log monitoring** (setup log rotation)

## Maintenance

### Update nginx config

```bash
# Edit config
sudo nano /etc/nginx/sites-available/jargas

# Test
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Restart nginx

```bash
sudo systemctl restart nginx
```

### Check nginx version

```bash
nginx -v
```

