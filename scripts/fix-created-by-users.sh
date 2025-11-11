#!/bin/bash

# Script untuk memperbaiki error login: Unknown column 'users.created_by'
# Script ini akan menambahkan kolom created_by ke tabel users
# Usage: ./fix-created-by-users.sh

# Default values
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-jargas_apbn}"
DB_PORT="${DB_PORT:-3306}"

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
    exit 1
fi

echo -e "${GREEN}📄 File SQL ditemukan: $SQL_FILE${NC}"
echo ""

# Build MySQL command
MYSQL_CMD="mysql"
MYSQL_ARGS=(
    -h "$DB_HOST"
    -P "$DB_PORT"
    -u "$DB_USER"
)

if [ -n "$DB_PASSWORD" ]; then
    MYSQL_ARGS+=(-p"$DB_PASSWORD")
fi

MYSQL_ARGS+=("$DB_NAME")

echo -e "${YELLOW}🔧 Menjalankan script SQL untuk menambahkan kolom created_by...${NC}"
echo -e "${GRAY}   Host: $DB_HOST${NC}"
echo -e "${GRAY}   Port: $DB_PORT${NC}"
echo -e "${GRAY}   Database: $DB_NAME${NC}"
echo ""

# Execute SQL file
if "$MYSQL_CMD" "${MYSQL_ARGS[@]}" < "$SQL_FILE"; then
    echo ""
    echo -e "${GREEN}✅ Script berhasil dijalankan!${NC}"
    echo -e "${GREEN}   Kolom created_by sudah ditambahkan ke tabel users.${NC}"
    echo ""
    echo -e "${GREEN}🎉 Error login seharusnya sudah teratasi!${NC}"
    echo -e "${GREEN}   Silakan coba login lagi sebagai admin.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Error saat menjalankan script SQL${NC}"
    exit 1
fi

