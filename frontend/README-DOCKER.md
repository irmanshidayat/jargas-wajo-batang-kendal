# Frontend - Setup dengan Docker

Dokumentasi untuk menjalankan frontend Jargas APBN dengan Docker (Backend tanpa Docker).

## 📋 Prasyarat

1. **Docker Desktop** (Windows/Mac) atau **Docker Engine** (Linux)
   - Download dari: https://www.docker.com/products/docker-desktop
   - Pastikan Docker berjalan

2. **Backend berjalan di host machine**
   - Backend harus berjalan tanpa Docker di `http://localhost:8000`
   - Gunakan script: `.\backend\run-local.ps1`
   - Atau manual: `cd backend && python run.py`

3. **Database XAMPP MySQL**
   - XAMPP MySQL harus berjalan di `localhost:3306`
   - Database sudah dibuat dan di-migrate

## 🚀 Quick Start

### 1. Pastikan Backend Berjalan

Backend harus berjalan di host machine sebelum menjalankan frontend:

```powershell
# Di terminal terpisah
cd backend
.\run-local.ps1
```

Backend akan berjalan di: **http://localhost:8000**

### 2. Build dan Jalankan Frontend dengan Docker

```powershell
# Dari root project
docker-compose -f docker-compose.frontend.yml up -d --build
```

**Atau step by step:**

```powershell
# Build image
docker-compose -f docker-compose.frontend.yml build

# Jalankan container
docker-compose -f docker-compose.frontend.yml up -d

# Cek status
docker-compose -f docker-compose.frontend.yml ps

# Cek logs
docker-compose -f docker-compose.frontend.yml logs -f
```

Frontend akan berjalan di: **http://localhost:8080**

### 3. Akses Aplikasi

- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔧 Konfigurasi

### Port Mapping

Default port frontend adalah `8080`. Untuk mengubah port, edit file `.env` di root project:

```env
FRONTEND_PORT_MAPPED=8080
```

Atau override saat menjalankan:

```powershell
FRONTEND_PORT_MAPPED=3000 docker-compose -f docker-compose.frontend.yml up -d
```

### API Base URL

Frontend menggunakan `VITE_API_BASE_URL` untuk API base URL. Default: `/api/v1`

Nginx akan mem-proxy request `/api/*` ke backend di `http://host.docker.internal:8000`.

**Catatan:** `host.docker.internal` adalah cara Docker mengakses host machine:
- ✅ **Windows/Mac Docker Desktop:** Sudah didukung secara default
- ⚠️ **Linux Docker Engine:** Mungkin perlu konfigurasi tambahan

## 🐛 Troubleshooting

### Error: Backend tidak dapat diakses

**Error:**
```
502 Bad Gateway
```

**Solusi:**
1. Pastikan backend berjalan di `http://localhost:8000`
2. Test backend: `curl http://localhost:8000/health`
3. Cek firewall tidak memblokir port 8000
4. Untuk Linux, mungkin perlu konfigurasi `host.docker.internal`

### Error: host.docker.internal tidak ditemukan (Linux)

**Error:**
```
nginx: [emerg] host not found in upstream "host.docker.internal"
```

**Solusi untuk Linux:**

**Opsi 1: Tambahkan extra_hosts di docker-compose (sudah ada)**
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Opsi 2: Gunakan IP host machine**
1. Cari IP host machine:
   ```bash
   ip addr show docker0 | grep inet
   ```
2. Update `nginx.conf`:
   ```nginx
   proxy_pass http://172.17.0.1:8000;  # Ganti dengan IP host Anda
   ```
3. Rebuild container:
   ```powershell
   docker-compose -f docker-compose.frontend.yml up -d --build
   ```

**Opsi 3: Gunakan network mode host (Linux only)**
```yaml
network_mode: "host"
```
⚠️ **Catatan:** Mode ini tidak kompatibel dengan port mapping.

### Error: Port sudah digunakan

**Error:**
```
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Solusi:**
1. Cek aplikasi lain yang menggunakan port 8080
2. Ubah port di `.env`: `FRONTEND_PORT_MAPPED=3000`
3. Atau stop aplikasi yang menggunakan port tersebut

### Error: Build gagal

**Error:**
```
npm install failed
```

**Solusi:**
1. Cek koneksi internet
2. Clear Docker build cache:
   ```powershell
   docker-compose -f docker-compose.frontend.yml build --no-cache
   ```
3. Cek log untuk detail error:
   ```powershell
   docker-compose -f docker-compose.frontend.yml build
   ```

### Error: Container tidak start

**Error:**
```
Container exited with code 1
```

**Solusi:**
1. Cek logs:
   ```powershell
   docker-compose -f docker-compose.frontend.yml logs frontend
   ```
2. Cek nginx configuration:
   ```powershell
   docker-compose -f docker-compose.frontend.yml exec frontend nginx -t
   ```
3. Rebuild container:
   ```powershell
   docker-compose -f docker-compose.frontend.yml up -d --build
   ```

## 📝 Command Reference

### Build Image

```powershell
# Build dengan cache
docker-compose -f docker-compose.frontend.yml build

# Build tanpa cache (fresh build)
docker-compose -f docker-compose.frontend.yml build --no-cache
```

### Run Container

```powershell
# Run di background (detached)
docker-compose -f docker-compose.frontend.yml up -d

# Run di foreground (lihat logs)
docker-compose -f docker-compose.frontend.yml up

# Run dan rebuild
docker-compose -f docker-compose.frontend.yml up -d --build
```

### Stop Container

```powershell
# Stop container
docker-compose -f docker-compose.frontend.yml stop

# Stop dan remove container
docker-compose -f docker-compose.frontend.yml down

# Stop, remove container dan volumes
docker-compose -f docker-compose.frontend.yml down -v
```

### View Logs

```powershell
# Logs terakhir
docker-compose -f docker-compose.frontend.yml logs

# Logs real-time (follow)
docker-compose -f docker-compose.frontend.yml logs -f

# Logs container tertentu
docker-compose -f docker-compose.frontend.yml logs frontend

# Logs dengan tail
docker-compose -f docker-compose.frontend.yml logs --tail=100
```

### Container Management

```powershell
# Cek status container
docker-compose -f docker-compose.frontend.yml ps

# Restart container
docker-compose -f docker-compose.frontend.yml restart

# Execute command di container
docker-compose -f docker-compose.frontend.yml exec frontend sh

# Test nginx config
docker-compose -f docker-compose.frontend.yml exec frontend nginx -t

# Reload nginx config
docker-compose -f docker-compose.frontend.yml exec frontend nginx -s reload
```

## 🔄 Development Workflow

### Development dengan Hot Reload

Untuk development dengan hot reload, gunakan Vite dev server (tanpa Docker):

```powershell
cd frontend
npm install
npm run dev
```

Frontend dev server akan berjalan di: **http://localhost:3000**

### Production Build dengan Docker

Untuk production build:

```powershell
# Build dan run
docker-compose -f docker-compose.frontend.yml up -d --build

# Atau build saja
docker-compose -f docker-compose.frontend.yml build
```

## 🌐 Network Configuration

### Akses dari Network Lain

Untuk mengakses frontend dari device lain di network yang sama:

1. Update `docker-compose.frontend.yml`:
   ```yaml
   ports:
     - "0.0.0.0:8080:80"  # Listen di semua interface
   ```

2. Akses dari device lain:
   ```
   http://<IP_HOST_MACHINE>:8080
   ```

### CORS Configuration

Pastikan backend CORS configuration mengizinkan origin frontend:

```env
# Di backend .env
CORS_ORIGINS=http://localhost:8080,http://localhost:3000,http://localhost:5173
```

## 📁 Struktur File

```
root/
├── docker-compose.frontend.yml    # Docker Compose untuk frontend
└── frontend/
    ├── Dockerfile                  # Multi-stage build (Node + Nginx)
    ├── nginx.conf                  # Nginx configuration (proxy ke host.docker.internal)
    ├── README-DOCKER.md            # Dokumentasi ini
    ├── package.json                # Dependencies
    ├── vite.config.ts              # Vite configuration
    └── src/                        # Source code
```

## 💡 Tips

1. **Hot Reload untuk Development**
   - Gunakan `npm run dev` untuk development dengan hot reload
   - Gunakan Docker untuk production build

2. **Backend Connection**
   - Pastikan backend berjalan sebelum frontend
   - Test backend: `curl http://localhost:8000/health`

3. **Network Issues (Linux)**
   - Jika `host.docker.internal` tidak bekerja, gunakan IP host machine
   - Atau gunakan `network_mode: host` (Linux only)

4. **Port Conflicts**
   - Gunakan port berbeda jika ada konflik
   - Cek port yang digunakan: `netstat -ano | findstr :8080` (Windows)

5. **Docker Resources**
   - Pastikan Docker memiliki cukup resources (RAM, CPU)
   - Monitor dengan: `docker stats`

## 🔗 Referensi

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Vite Documentation](https://vitejs.dev/)

---

**Selamat Development! 🚀**

