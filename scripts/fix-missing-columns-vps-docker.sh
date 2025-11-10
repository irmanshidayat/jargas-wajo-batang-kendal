#!/bin/bash

# Script untuk memperbaiki kolom yang missing di database VPS (via Docker)
# Script ini akan menambahkan kolom-kolom yang diperlukan untuk DELETE user
# Usage: ./fix-missing-columns-vps-docker.sh

# Default values
DB_CONTAINER="${DB_CONTAINER:-jargas_mysql}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-admin123}"
DB_NAME="${DB_NAME:-jargas_apbn}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Fix Missing Columns di Database VPS${NC}"
echo -e "${CYAN}(via Docker Container)${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQL_FILE="$SCRIPT_DIR/fix_missing_columns_vps.sql"

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}❌ File SQL tidak ditemukan: $SQL_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}📄 File SQL ditemukan: $SQL_FILE${NC}"
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker tidak ditemukan. Pastikan Docker sudah terinstall.${NC}"
    exit 1
fi

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo -e "${RED}❌ Container ${DB_CONTAINER} tidak ditemukan.${NC}"
    echo -e "${YELLOW}   Container yang tersedia:${NC}"
    docker ps -a --format '{{.Names}}' | sed 's/^/   - /'
    exit 1
fi

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo -e "${YELLOW}⚠️  Container ${DB_CONTAINER} tidak berjalan. Mencoba start...${NC}"
    docker start "${DB_CONTAINER}"
    sleep 3
fi

echo -e "${YELLOW}🔧 Menjalankan script SQL via Docker...${NC}"
echo -e "${GRAY}   Container: $DB_CONTAINER${NC}"
echo -e "${GRAY}   Database: $DB_NAME${NC}"
echo ""

# Execute SQL file via Docker
if docker exec -i "${DB_CONTAINER}" mysql -u"${DB_USER}" -p"${DB_PASSWORD}" "${DB_NAME}" < "$SQL_FILE"; then
    echo ""
    echo -e "${GREEN}✅ Script berhasil dijalankan!${NC}"
    echo -e "${GREEN}   Kolom-kolom yang diperlukan sudah ditambahkan ke database.${NC}"
    echo ""
    echo -e "${CYAN}📋 Kolom yang ditambahkan:${NC}"
    echo -e "   - surat_permintaans.status"
    echo -e "   - surat_jalans.nomor_surat_permintaan"
    echo -e "   - surat_jalans.nomor_barang_keluar"
    echo -e "   - surat_jalans.stock_out_id"
    echo ""
    echo -e "${GREEN}🎉 Sekarang fitur DELETE user seharusnya sudah berfungsi!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Error saat menjalankan script SQL${NC}"
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo -e "   - Pastikan container ${DB_CONTAINER} berjalan"
    echo -e "   - Cek username dan password database"
    echo -e "   - Cek nama database: ${DB_NAME}"
    exit 1
fi

