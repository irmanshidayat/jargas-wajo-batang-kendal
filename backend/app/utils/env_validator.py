"""
Utility untuk memvalidasi format file .env
"""
import re
from pathlib import Path
from typing import List, Tuple


def validate_env_file(env_path: str = ".env") -> Tuple[bool, List[str]]:
    """
    Validasi format file .env
    
    Args:
        env_path: Path ke file .env
        
    Returns:
        Tuple (is_valid, list_of_errors)
    """
    errors = []
    env_file = Path(env_path)
    
    if not env_file.exists():
        return True, []  # File tidak ada, tidak perlu validasi
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            
            # Skip baris kosong dan komentar
            if not line or line.startswith('#'):
                continue
            
            # Cek jika ada spasi di sekitar tanda =
            if '=' in line:
                # Cek lebih spesifik: spasi sebelum atau setelah =
                if re.search(r'\s+=\s*|\s*=\s+', line):
                    key_part = line.split('=')[0].strip()
                    errors.append(
                        f"Line {line_num}: Jangan ada spasi di sekitar tanda =\n"
                        f"  Ditemukan: {line[:60]}\n"
                        f"  Format yang benar: {key_part}=value (tanpa spasi)"
                    )
            
            # Cek jika ada tanda = tapi bukan format KEY=value yang valid
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) != 2:
                    errors.append(
                        f"Line {line_num}: Format tidak valid\n"
                        f"  Ditemukan: {line[:50]}"
                    )
                elif not parts[0].strip() or not parts[1].strip():
                    errors.append(
                        f"Line {line_num}: KEY atau VALUE kosong\n"
                        f"  Ditemukan: {line[:50]}"
                    )
    
    except Exception as e:
        errors.append(f"Error membaca file .env: {str(e)}")
    
    return len(errors) == 0, errors


def print_env_validation_warnings():
    """Print warning jika ada masalah dengan file .env"""
    is_valid, errors = validate_env_file()
    
    if not is_valid and errors:
        print("\n" + "="*60)
        print("⚠️  PERINGATAN: Masalah format di file .env")
        print("="*60)
        for error in errors:
            print(f"\n{error}")
        print("\n" + "="*60)
        print("💡 Tips: Periksa file .env dan pastikan format:")
        print("   ✅ Benar: KEY=value")
        print("   ❌ Salah: KEY = value (ada spasi)")
        print("="*60 + "\n")

