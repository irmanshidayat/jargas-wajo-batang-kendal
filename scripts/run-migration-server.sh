#!/bin/bash
# Script untuk menjalankan migration di server
# Digunakan jika auto-migrate tidak berjalan atau perlu manual migration

set -e

PROJECT_PATH="${1:-~/jargas-wajo-batang-kendal}"

echo "=========================================="
echo "Jalankan Database Migration"
echo "=========================================="
echo ""

cd "$PROJECT_PATH" || exit 1

echo "Step 1: Cek status migration saat ini..."
docker-compose exec -T backend alembic current || echo "⚠️  Belum ada migration yang dijalankan"

echo ""
echo "Step 2: Cek migration yang tersedia..."
docker-compose exec -T backend alembic history | head -20 || echo "⚠️  Tidak bisa cek history"

echo ""
echo "Step 3: Jalankan migration ke head..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "Step 4: Verifikasi migration berhasil..."
docker-compose exec -T backend alembic current

echo ""
echo "Step 5: Verifikasi tabel database..."
docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;" 2>/dev/null | head -30

echo ""
echo "=========================================="
echo "✅ Migration selesai!"
echo "=========================================="
echo ""

