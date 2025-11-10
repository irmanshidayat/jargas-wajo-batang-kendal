"""
Configuration untuk auto-generate pages dari routes dan menu items.
Pages akan otomatis dibuat saat backend startup jika belum ada.
"""

# Mapping path ke display name dan metadata
# Struktur: {path: {"name": "...", "display_name": "...", "icon": "...", "order": ...}}
PAGES_CONFIG = [
    # Dashboard & Main
    {
        "name": "dashboard",
        "path": "/dashboard",
        "display_name": "Dashboard",
        "icon": "dashboard",
        "order": 1,
    },
    {
        "name": "inventory",
        "path": "/inventory",
        "display_name": "Dashboard Inventory",
        "icon": "inventory",
        "order": 2,
    },
    # Inventory - Stock Management
    {
        "name": "stock_in",
        "path": "/inventory/stock-in",
        "display_name": "Barang Masuk",
        "icon": "stock-in",
        "order": 3,
    },
    {
        "name": "stock_in_list",
        "path": "/inventory/stock-in/list",
        "display_name": "Daftar Barang Masuk",
        "icon": "list",
        "order": 4,
    },
    {
        "name": "stock_out",
        "path": "/inventory/stock-out",
        "display_name": "Barang Keluar",
        "icon": "stock-out",
        "order": 5,
    },
    {
        "name": "stock_out_list",
        "path": "/inventory/stock-out/list",
        "display_name": "Daftar Barang Keluar",
        "icon": "list",
        "order": 6,
    },
    # Inventory - Master Data
    {
        "name": "materials",
        "path": "/inventory/materials",
        "display_name": "Master Material",
        "icon": "materials",
        "order": 7,
    },
    {
        "name": "mandors",
        "path": "/inventory/mandors",
        "display_name": "Master Mandor",
        "icon": "mandors",
        "order": 8,
    },
    # Inventory - Operations
    {
        "name": "installed",
        "path": "/inventory/installed",
        "display_name": "Barang Terpasang",
        "icon": "installed",
        "order": 9,
    },
    {
        "name": "installed_create",
        "path": "/inventory/installed/create",
        "display_name": "Tambah Barang Terpasang",
        "icon": "add",
        "order": 10,
    },
    {
        "name": "returns",
        "path": "/inventory/returns",
        "display_name": "Retur Barang",
        "icon": "returns",
        "order": 11,
    },
    {
        "name": "returns_create",
        "path": "/inventory/returns/create",
        "display_name": "Tambah Retur Barang",
        "icon": "add",
        "order": 12,
    },
    {
        "name": "surat_permintaan",
        "path": "/inventory/surat-permintaan",
        "display_name": "Surat Permintaan",
        "icon": "document",
        "order": 13,
    },
    {
        "name": "surat_permintaan_list",
        "path": "/inventory/surat-permintaan/list",
        "display_name": "Daftar Surat Permintaan",
        "icon": "list",
        "order": 14,
    },
    {
        "name": "surat_jalan",
        "path": "/inventory/surat-jalan",
        "display_name": "Surat Jalan",
        "icon": "document",
        "order": 15,
    },
    {
        "name": "surat_jalan_list",
        "path": "/inventory/surat-jalan/list",
        "display_name": "Daftar Surat Jalan",
        "icon": "list",
        "order": 16,
    },
    # User Management
    {
        "name": "user_management",
        "path": "/user-management",
        "display_name": "User dan Role Management",
        "icon": "users",
        "order": 17,
    },
    {
        "name": "user_management_users",
        "path": "/user-management/users",
        "display_name": "Manajemen User",
        "icon": "user-list",
        "order": 18,
    },
    {
        "name": "user_management_roles",
        "path": "/user-management/roles",
        "display_name": "Manajemen Role",
        "icon": "role",
        "order": 19,
    },
    {
        "name": "user_management_permissions",
        "path": "/user-management/permissions",
        "display_name": "Manajemen Permissions",
        "icon": "permissions",
        "order": 20,
    },
]

