# 🗑️ Tutorial Menghapus Data Database - Jargas APBN

Dokumentasi singkat untuk menghapus semua data dari database `jargas_apbn` di server VPS, **kecuali** tabel yang dilindungi.

## 📋 Tabel yang Dilindungi (TIDAK akan dihapus)

- ✅ `users` - Data pengguna
- ✅ `roles` - Data role/peran
- ✅ `pages` - Data halaman/menu
- ✅ `permissions` - Data permission/izin

## 🚀 Cara Penggunaan

### Metode 1: Via PowerShell Script (Recommended)

**Lokal (Windows):**

```powershell
cd "C:\Irman\Coding Jargas APBN\Jargas APBN"
.\scripts\active\clear-database-vps.ps1
```

**Langkah-langkah:**
1. Script akan meminta konfirmasi pertama (ketik `y`)
2. Script akan cek koneksi ke server VPS
3. Script akan cek status container backend
4. Script akan memastikan file Python ada di server (jika belum, akan copy otomatis)
5. Script Python akan meminta konfirmasi kedua (ketik `YA` untuk konfirmasi)
6. Proses penghapusan akan berjalan

### Metode 2: Langsung di Server VPS

**Via SSH:**

```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
docker-compose exec backend python -m scripts.clear_database_except_users
```

**Konfirmasi:**
- Ketik `YA` (huruf besar semua) untuk melanjutkan penghapusan

## 📊 Tabel yang Akan Dihapus

Script akan menghapus data dari tabel berikut (dalam urutan yang benar):

### 1. Tabel Child/Detail Items
- `surat_jalan_items`
- `surat_permintaan_items`
- `user_permissions`
- `user_menu_preferences`
- `role_permissions`
- `user_projects`

### 2. Tabel Transaksi/Inventory
- `notifications`
- `audit_logs`
- `returns`
- `installed`
- `stock_outs`
- `stock_ins`
- `surat_jalans`
- `surat_permintaans`

### 3. Tabel Master Data
- `materials`
- `mandors`
- `projects`

## ⚠️ Peringatan Penting

1. **Operasi TIDAK DAPAT DIBATALKAN** setelah dikonfirmasi
2. **Semua data akan dihapus PERMANEN** (kecuali tabel yang dilindungi)
3. **Pastikan sudah backup** jika diperlukan
4. **Konfirmasi ganda** diperlukan untuk keamanan

## ✅ Verifikasi Hasil

Setelah proses selesai, verifikasi data yang tersisa:

```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e "SELECT COUNT(*) as users_count FROM users;"
```

Atau cek semua tabel yang masih ada data:

```bash
docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e "SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = 'jargas_apbn' AND table_rows > 0 ORDER BY table_name;"
```

## 🔧 Troubleshooting

### Error: "No module named scripts.clear_database_except_users"

**Solusi:**
1. Pastikan file `backend/scripts/clear_database_except_users.py` ada di server
2. Copy file manual jika perlu:
   ```powershell
   scp backend\scripts\clear_database_except_users.py root@72.61.142.109:~/jargas-wajo-batang-kendal/backend/scripts/
   ```
3. Rebuild container backend:
   ```bash
   ssh root@72.61.142.109
   cd ~/jargas-wajo-batang-kendal
   docker-compose build --no-cache backend
   docker-compose up -d backend
   ```

### Error: "Container backend tidak berjalan"

**Solusi:**
```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
docker-compose up -d backend
```

### Error Koneksi SSH

**Solusi:**
- Pastikan SSH key sudah terkonfigurasi
- Atau gunakan password authentication
- Cek koneksi jaringan ke server VPS

## 📝 Catatan

- Script menggunakan `SET FOREIGN_KEY_CHECKS = 0` sementara untuk performa
- Foreign key checks akan diaktifkan kembali setelah proses selesai
- Rollback otomatis jika terjadi error
- Statistik lengkap ditampilkan sebelum dan sesudah penghapusan

## 🔗 File Terkait

- Script Python: `backend/scripts/clear_database_except_users.py`
- Script PowerShell: `scripts/clear-database-vps.ps1`

