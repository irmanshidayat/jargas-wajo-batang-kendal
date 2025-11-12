# Dokumentasi Akses Web dari Jaringan Lokal

Dokumentasi ini menjelaskan cara mengkonfigurasi aplikasi agar bisa diakses dari perangkat lain di jaringan lokal yang sama.

## 📋 Daftar Isi
1. [Cara Mencari IP Laptop](#cara-mencari-ip-laptop)
2. [Menambahkan IP ke Konfigurasi](#menambahkan-ip-ke-konfigurasi)
3. [Cara Akses dari Perangkat Lain](#cara-akses-dari-perangkat-lain)
4. [Troubleshooting](#troubleshooting)

---

## 🔍 Cara Mencari IP Laptop

### Metode 1: Menggunakan Command Prompt / PowerShell

1. Buka **Command Prompt** atau **PowerShell**
   - Tekan `Win + R`, ketik `cmd` atau `powershell`, lalu Enter

2. Jalankan perintah:
   ```bash
   ipconfig /all
   ```

3. Cari bagian **"Wireless LAN adapter Wi-Fi"** atau **"Ethernet adapter"**
   - Lihat **IPv4 Address** (bukan yang "vEthernet" atau "WSL")
   - Contoh: `192.168.1.243`

### Metode 2: Menggunakan Settings Windows

1. Buka **Settings** → **Network & Internet** → **Wi-Fi** (atau **Ethernet**)
2. Klik nama jaringan yang sedang terhubung
3. Scroll ke bawah, lihat **"IPv4 address"**

### Metode 3: Menggunakan PowerShell (Detail)

Jalankan perintah di PowerShell:
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"}
```

---

## ⚙️ Menambahkan IP ke Konfigurasi.

Setelah mendapatkan IP laptop, ikuti langkah berikut:

### 1. Update Backend CORS Configuration

Edit file: `backend/app/config/settings.py`

Cari baris yang berisi:
```python
CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://192.168.1.243:3000"
```

**Tambahkan IP baru** dengan format: `http://IP_BARU:3000`

**Contoh:**
Jika IP laptop Anda adalah `192.168.1.100`, ubah menjadi:
```python
CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://192.168.1.243:3000,http://192.168.1.100:3000"
```

**Catatan:** 
- Pisahkan setiap IP dengan koma (`,`)
- Format: `http://IP_ADDRESS:3000`
- Port `3000` adalah port frontend

### 2. Update via Environment Variable (Opsional)

Alternatifnya, Anda bisa menambahkan di file `.env`:

1. Buat atau edit file `.env` di folder `backend/`
2. Tambahkan baris:
   ```env
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.1.243:3000,http://192.168.1.100:3000
   ```

**Keuntungan menggunakan `.env`:**
- Tidak perlu edit kode Python
- Lebih mudah diubah
- Bisa berbeda per environment

### 3. Restart Backend

Setelah mengubah konfigurasi, **restart backend server**:

```bash
# Hentikan server yang sedang berjalan (Ctrl + C)
# Kemudian jalankan lagi:
python run.py
```

---

## 🌐 Cara Akses dari Perangkat Lain

### Prasyarat

1. ✅ Laptop dan perangkat lain harus terhubung ke **Wi-Fi yang sama**
2. ✅ Backend server sudah berjalan di laptop
3. ✅ Frontend server sudah berjalan di laptop
4. ✅ Firewall Windows tidak memblokir port 3000 dan 8000

### Langkah Akses

1. **Buka browser** di perangkat lain (handphone, tablet, atau laptop lain)

2. **Akses URL:**
   ```
   http://IP_LAPTOP:3000
   ```
   
   Contoh:
   ```
   http://192.168.1.243:3000
   ```

3. Website akan muncul dan bisa digunakan seperti biasa

### Port yang Digunakan

- **Frontend:** Port `3000` (http://IP:3000)
- **Backend API:** Port `8000` (http://IP:8000) - biasanya tidak perlu diakses langsung

---

## 🔧 Troubleshooting

### ❌ Tidak bisa akses dari perangkat lain

**1. Cek koneksi jaringan**
- Pastikan perangkat lain terhubung ke Wi-Fi yang sama
- Coba ping dari perangkat lain:
  ```bash
  ping 192.168.1.243
  ```

**2. Cek firewall Windows**
- Buka **Windows Defender Firewall**
- Pastikan port 3000 dan 8000 tidak diblokir
- Atau sementara nonaktifkan firewall untuk testing

**3. Cek apakah server sudah berjalan**
- Backend: Pastikan terminal menampilkan `Uvicorn running on http://0.0.0.0:8000`
- Frontend: Pastikan terminal menampilkan `Local: http://localhost:3000`

**4. Cek IP apakah sudah benar**
- IP bisa berubah jika laptop disconnect/reconnect Wi-Fi
- Jalankan `ipconfig` lagi untuk cek IP terbaru

### ❌ CORS Error di browser

**Error:** `Access to fetch at 'http://192.168.1.243:8000/api/...' from origin 'http://192.168.1.243:3000' has been blocked by CORS policy`

**Solusi:**
1. Pastikan IP sudah ditambahkan di `CORS_ORIGINS` di `settings.py`
2. Restart backend server setelah mengubah konfigurasi
3. Hard refresh browser (Ctrl + Shift + R)

### ❌ IP berubah setiap kali connect Wi-Fi

**Masalah:** IP laptop berubah karena DHCP

**Solusi 1: Set IP Static (Recommended)**
1. Buka **Settings** → **Network & Internet** → **Wi-Fi**
2. Klik **Properties** pada jaringan aktif
3. Scroll ke **IP settings**
4. Klik **Edit** → pilih **Manual**
5. Set IP static (misalnya: `192.168.1.100`)
6. Set Subnet mask: `255.255.255.0`
7. Set Gateway: `192.168.1.1` (sesuai router Anda)

**Solusi 2: Gunakan Wildcard CORS (Development Only)**
Edit `settings.py` untuk menerima semua IP di subnet:
```python
# HATI-HATI: Ini kurang aman untuk production!
CORS_ORIGINS: Union[str, List[str]] = "*"
```

**Solusi 3: Update IP secara berkala**
- Setiap kali IP berubah, update `CORS_ORIGINS` di `settings.py`
- Restart backend

### ❌ Frontend tidak bisa connect ke backend

**Error:** Network error atau connection refused

**Solusi:**
1. Pastikan backend sudah berjalan di port 8000
2. Cek proxy di `vite.config.ts` masih menunjuk ke `http://localhost:8000` (ini sudah benar)
3. Pastikan `host: '0.0.0.0'` sudah ada di `vite.config.ts`

---

## 📝 Catatan Penting

1. **Keamanan:**
   - Konfigurasi ini hanya untuk **development/testing**
   - Untuk production, gunakan HTTPS dan konfigurasi keamanan yang lebih ketat

2. **IP Address:**
   - IP bisa berubah jika laptop disconnect/reconnect Wi-Fi
   - Gunakan IP static untuk stabilitas jangka panjang

3. **Port:**
   - Port 3000 (frontend) dan 8000 (backend) harus terbuka
   - Pastikan tidak ada aplikasi lain yang menggunakan port tersebut

4. **Performance:**
   - Akses dari jaringan lokal biasanya cepat
   - Jika lambat, cek kualitas koneksi Wi-Fi

---

## 🔄 Quick Reference

### Menambahkan IP Baru (Quick Steps)

1. Cari IP: `ipconfig` → lihat IPv4 Address di Wi-Fi adapter
2. Edit: `backend/app/config/settings.py` → tambahkan `http://IP_BARU:3000` ke `CORS_ORIGINS`
3. Restart: Backend server
4. Akses: `http://IP_BARU:3000` dari perangkat lain

### Format CORS Origins

```python
CORS_ORIGINS = "http://localhost:3000,http://localhost:5173,http://192.168.1.243:3000,http://192.168.1.100:3000"
```

**Format:** `http://IP_ADDRESS:PORT`
**Pemisah:** Koma (`,`)
**Spasi:** Optional setelah koma

---

## 📞 Bantuan Lebih Lanjut

Jika masih mengalami masalah:
1. Cek log backend di terminal
2. Cek log browser console (F12)
3. Pastikan semua langkah sudah diikuti dengan benar
4. Restart semua server dan coba lagi

---

**Last Updated:** November 2024
**Version:** 1.0.0

