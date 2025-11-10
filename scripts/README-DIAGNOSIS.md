# Script Diagnosis Docker Migration

Script-script ini dibuat untuk membantu mendiagnosis masalah migration di server.

## Script yang Tersedia

### 1. `check-docker-logs-server.ps1`
Script untuk mengecek log docker di server dan melihat error lengkap.

**Penggunaan:**
```powershell
# Cek log terakhir 200 baris
.\check-docker-logs-server.ps1

# Cek log real-time (Ctrl+C untuk stop)
.\check-docker-logs-server.ps1 -Follow

# Hanya tampilkan error
.\check-docker-logs-server.ps1 -ErrorsOnly

# Custom jumlah baris
.\check-docker-logs-server.ps1 -Lines 500
```

**Parameter:**
- `-ServerIP`: IP server (default: 72.61.142.109)
- `-Username`: Username SSH (default: root)
- `-ProjectPath`: Path project di server (default: ~/jargas-wajo-batang-kendal)
- `-Lines`: Jumlah baris log (default: 200)
- `-Follow`: Follow log real-time
- `-ErrorsOnly`: Hanya tampilkan error

### 2. `check-container-status-server.ps1`
Script untuk mengecek status container dan restart count.

**Penggunaan:**
```powershell
.\check-container-status-server.ps1
```

**Output:**
- Status semua container
- Detail status backend container
- Restart count (jika > 10 akan warning)
- Health status
- Log terakhir (10 baris)

## Masalah yang Sudah Diperbaiki

### 1. Migration Tabel Users
- ✅ Dibuat migration baru `80cb2c36260b_create_users_table.py` untuk membuat tabel users
- ✅ Migration ini dijalankan sebelum migration `82b36e17b6fd` yang membutuhkan tabel users

### 2. Perbaikan Migration 82b36e17b6fd
- ✅ Ditambahkan validasi untuk memastikan tabel `users` sudah ada sebelum membuat `user_projects`
- ✅ Ditambahkan logging yang lebih detail untuk tracking progress
- ✅ Ditambahkan error handling yang lebih baik
- ✅ Ditambahkan validasi untuk memastikan tabel `projects` sudah ada sebelum membuat foreign key

### 3. Urutan Migration
Urutan migration sekarang:
1. `2bcb46d867a0` (base)
2. `add_surat_permohonan_stock_outs`
3. `80cb2c36260b` ← **Membuat tabel users**
4. `82b36e17b6fd` ← **Membutuhkan tabel users**

## Cara Menggunakan

### Step 1: Cek Log Error
```powershell
.\check-docker-logs-server.ps1 -ErrorsOnly
```

### Step 2: Cek Status Container
```powershell
.\check-container-status-server.ps1
```

### Step 3: Jika Ada Masalah
1. Cek log lengkap: `.\check-docker-logs-server.ps1 -Follow`
2. Cek restart count: `.\check-container-status-server.ps1`
3. Jika restart count tinggi (>10), kemungkinan ada error yang menyebabkan container crash

### Step 4: Rebuild dan Restart
Setelah memperbaiki migration, rebuild container:
```powershell
# Di server
cd ~/jargas-wajo-batang-kendal
docker-compose build backend
docker-compose up -d backend
```

## Troubleshooting

### Migration Berulang Terus
**Penyebab:**
- Migration gagal tapi tidak ter-commit ke `alembic_version`
- Container restart terus karena error

**Solusi:**
1. Cek log error: `.\check-docker-logs-server.ps1 -ErrorsOnly`
2. Cek restart count: `.\check-container-status-server.ps1`
3. Jika restart count tinggi, cek log untuk error yang menyebabkan crash

### Tabel Users Belum Ada
**Penyebab:**
- Migration untuk membuat tabel users belum dijalankan
- Migration chain tidak lengkap

**Solusi:**
1. Pastikan migration `80cb2c36260b_create_users_table.py` sudah ada
2. Jalankan migration manual: `docker-compose exec backend alembic upgrade head`

### Foreign Key Error
**Penyebab:**
- Tabel yang direferensikan belum ada
- Urutan migration salah

**Solusi:**
1. Pastikan urutan migration benar (cek dengan `alembic history`)
2. Migration `80cb2c36260b` harus dijalankan sebelum `82b36e17b6fd`

## Catatan Penting

- Migration `80cb2c36260b` akan membuat tabel users jika belum ada
- Migration `82b36e17b6fd` akan error jika tabel users belum ada (dengan error message yang jelas)
- Semua migration sekarang memiliki logging yang lebih detail untuk tracking

