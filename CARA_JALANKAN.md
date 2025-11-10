# 🚀 Cara Menjalankan Setup Nginx Host

## Opsi 1: Langsung di Server SSH (Paling Mudah)

**Langkah 1:** Buka terminal SSH dan masuk ke server
```bash
ssh username@server-ip
cd ~/jargas-wajo-batang-kendal
```

**Langkah 2:** Jalankan salah satu perintah berikut:

### A. Menggunakan Script Otomatis (Recommended)
```bash
bash nginx-host/run-setup.sh
```

### B. Copy-Paste Perintah Langsung
```bash
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas && \
sudo ln -sf /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl reload nginx && \
echo "✅ Setup selesai!" && \
curl http://localhost/health
```

---

## Opsi 2: Dari Windows (Menggunakan PowerShell)

**Langkah 1:** Buka PowerShell di Windows

**Langkah 2:** Jalankan script:
```powershell
.\nginx-host\setup-from-windows.ps1 -ServerIP "your-server-ip" -Username "your-username"
```

**Contoh:**
```powershell
.\nginx-host\setup-from-windows.ps1 -ServerIP "192.168.1.100" -Username "root"
```

**Jika menggunakan SSH Key:**
```powershell
.\nginx-host\setup-from-windows.ps1 -ServerIP "your-server-ip" -Username "your-username" -SSHKey "C:\path\to\key.pem"
```

---

## Opsi 3: Dari Windows (Menggunakan Batch File)

**Langkah 1:** Double-click file `JALANKAN_SETUP.bat`

**Langkah 2:** Ikuti instruksi yang muncul:
- Masukkan IP Server
- Masukkan Username SSH
- Masukkan path project (atau tekan Enter untuk default)

---

## Opsi 4: Manual Step-by-Step

Jika semua opsi di atas tidak bekerja, ikuti langkah manual:

### 1. Copy File ke Server
```bash
# Di server SSH
cd ~/jargas-wajo-batang-kendal
ls nginx-host/jargas.conf  # Pastikan file ada
```

### 2. Copy ke Nginx
```bash
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas
```

### 3. Buat Symbolic Link
```bash
sudo ln -s /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas
```

### 4. Hapus Default Config
```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

### 5. Test Konfigurasi
```bash
sudo nginx -t
```

### 6. Reload Nginx
```bash
sudo systemctl reload nginx
```

### 7. Verifikasi
```bash
sudo systemctl status nginx
curl http://localhost/health
```

---

## Setelah Setup Berhasil

### 1. Rebuild Container Frontend
```bash
cd ~/jargas-wajo-batang-kendal
docker-compose build frontend
docker-compose up -d frontend
docker-compose ps
```

### 2. Test Akses
```bash
# Test health check
curl http://localhost/health

# Test frontend
curl http://localhost/

# Test backend API
curl http://localhost/api/v1/health
```

### 3. Edit Domain (Jika Ada)
```bash
sudo nano /etc/nginx/sites-available/jargas
# Ubah: server_name _; menjadi server_name your-domain.com;
sudo nginx -t && sudo systemctl reload nginx
```

---

## Troubleshooting

### ❌ "Permission denied"
```bash
# Pastikan menggunakan sudo
sudo bash nginx-host/run-setup.sh
```

### ❌ "File tidak ditemukan"
```bash
# Pastikan berada di direktori project
cd ~/jargas-wajo-batang-kendal
pwd
ls nginx-host/jargas.conf
```

### ❌ "Nginx config error"
```bash
# Check error detail
sudo nginx -t
sudo cat /var/log/nginx/error.log
```

### ❌ "Port 80 sudah digunakan"
```bash
# Check apa yang menggunakan port 80
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# Stop service yang menggunakan port 80 (hati-hati!)
# sudo systemctl stop apache2  # contoh
```

### ❌ "Container tidak bisa diakses"
```bash
# Check container status
docker-compose ps

# Check port mapping
docker-compose port frontend 80
docker-compose port backend 8000

# Restart container
docker-compose restart frontend
```

---

## ✅ Checklist Setelah Setup

- [ ] Nginx config valid (`sudo nginx -t`)
- [ ] Nginx running (`sudo systemctl status nginx`)
- [ ] Health check berhasil (`curl http://localhost/health`)
- [ ] Frontend accessible (`curl http://localhost/`)
- [ ] Container frontend healthy (`docker-compose ps`)
- [ ] Domain dikonfigurasi (jika ada)
- [ ] SSL setup (jika ada domain)

---

## 📞 Butuh Bantuan?

Jika masih ada masalah, cek:
1. `SETUP_NGINX_HOST.md` - Dokumentasi lengkap
2. `nginx-host/README.md` - Dokumentasi nginx host
3. Log nginx: `sudo tail -f /var/log/nginx/jargas_error.log`

