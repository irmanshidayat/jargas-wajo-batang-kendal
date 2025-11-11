#!/bin/bash

# Script untuk memperbaiki error login: Unknown column 'users.created_by'
# Script ini dijalankan DI SERVER VPS (bukan dari Windows)
# Usage: ./fix-created-by-vps-server.sh

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
echo -e "${CYAN}Fix Error Login: created_by Column${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQL_FILE="$SCRIPT_DIR/fix_created_by_users.sql"

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}❌ File SQL tidak ditemukan: $SQL_FILE${NC}"
    echo -e "${YELLOW}   Pastikan file fix_created_by_users.sql ada di folder scripts${NC}"
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

echo -e "${YELLOW}🔧 Menjalankan script SQL untuk menambahkan kolom created_by...${NC}"
echo -e "${GRAY}   Container: $DB_CONTAINER${NC}"
echo -e "${GRAY}   Database: $DB_NAME${NC}"
echo ""

# Execute SQL file via Docker
if docker exec -i "${DB_CONTAINER}" mysql -u"${DB_USER}" -p"${DB_PASSWORD}" "${DB_NAME}" < "$SQL_FILE"; then
    echo ""
    echo -e "${GREEN}✅ Script berhasil dijalankan!${NC}"
    echo ""
    
    # Verify column exists
    echo -e "${YELLOW}🔍 Verifikasi kolom created_by...${NC}"
    if docker exec -i "${DB_CONTAINER}" mysql -u"${DB_USER}" -p"${DB_PASSWORD}" "${DB_NAME}" -e "DESCRIBE users;" 2>/dev/null | grep -q "created_by"; then
        echo -e "${GREEN}✅ Kolom created_by berhasil ditambahkan!${NC}"
        docker exec -i "${DB_CONTAINER}" mysql -u"${DB_USER}" -p"${DB_PASSWORD}" "${DB_NAME}" -e "DESCRIBE users;" 2>/dev/null | grep "created_by"
    else
        echo -e "${YELLOW}⚠️  Kolom created_by belum terdeteksi${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Error login seharusnya sudah teratasi!${NC}"
    echo -e "${GREEN}   Silakan coba login lagi sebagai admin.${NC}"
    echo ""
    echo -e "${CYAN}💡 Tips:${NC}"
    echo -e "   Jika masih error, restart backend container:"
    echo -e "   docker-compose restart backend"
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

