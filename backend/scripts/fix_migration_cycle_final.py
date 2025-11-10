"""Script untuk memperbaiki cycle dependency dengan pendekatan yang benar"""
import re
from pathlib import Path

def fix_cycle():
    """Memperbaiki cycle dengan membuat chain yang benar"""
    
    # Chain yang benar berdasarkan urutan logis:
    # 1. 2bcb46d867a0 (2025-10-31 22:37) - awal
    # 2. add_surat_permohonan_stock_outs (2025-10-31 22:48) - setelah 2bcb46d867a0
    # 3. 82b36e17b6fd (2025-01-15) - setelah add_surat_permohonan_stock_outs (tapi tanggal salah, seharusnya setelah)
    # 4. create_surat_jalan_tables (2025-01-20) - setelah 82b36e17b6fd
    # 5. 309b15867534 (2025-11-01) - setelah create_surat_jalan_tables
    # 6. ddf3b77ebeb4 (2025-11-03) - setelah 82b36e17b6fd
    
    fixes = {
        '2bcb46d867a0': None,  # Awal chain, tidak bergantung pada apapun (atau bergantung pada migration base)
        'add_surat_permohonan_stock_outs': '2bcb46d867a0',
        '82b36e17b6fd': 'add_surat_permohonan_stock_outs',
        'create_surat_jalan_tables': '82b36e17b6fd',
        '309b15867534': 'create_surat_jalan_tables',
        'ddf3b77ebeb4': '82b36e17b6fd',
    }
    
    migrations_dir = Path(__file__).parent.parent / "migrations" / "versions"
    
    for file in migrations_dir.glob("*.py"):
        content = file.read_text(encoding='utf-8')
        rev_match = re.search(r"revision:\s*str\s*=\s*['\"]([^'\"]+)['\"]", content)
        
        if not rev_match:
            continue
            
        revision = rev_match.group(1)
        
        if revision in fixes:
            new_down = fixes[revision]
            
            # Update down_revision
            old_pattern = r"down_revision:\s*Union\[str,\s*None\]\s*=\s*['\"]([^'\"]*)['\"]"
            if new_down:
                new_content = re.sub(old_pattern, f"down_revision: Union[str, None] = '{new_down}'", content)
            else:
                new_content = re.sub(old_pattern, "down_revision: Union[str, None] = None", content)
            
            # Update comment
            comment_pattern = r"Revises:\s*[^\n]+"
            if new_down:
                new_content = re.sub(comment_pattern, f"Revises: {new_down}", new_content)
            else:
                new_content = re.sub(comment_pattern, "Revises: (base)", new_content)
            
            file.write_text(new_content, encoding='utf-8')
            print(f"Fixed {revision} -> {new_down or 'None'}")

if __name__ == "__main__":
    fix_cycle()

