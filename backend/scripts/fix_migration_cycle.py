"""Script untuk memperbaiki cycle dependency di migration"""
import os
import re
from pathlib import Path
from datetime import datetime

def get_migration_info():
    """Mendapatkan info semua migration"""
    migrations_dir = Path(__file__).parent.parent / "migrations" / "versions"
    
    migrations = []
    
    for file in migrations_dir.glob("*.py"):
        content = file.read_text(encoding='utf-8')
        
        # Extract revision
        rev_match = re.search(r"revision:\s*str\s*=\s*['\"]([^'\"]+)['\"]", content)
        if not rev_match:
            continue
            
        revision = rev_match.group(1)
        
        # Extract down_revision
        down_match = re.search(r"down_revision:\s*Union\[str,\s*None\]\s*=\s*['\"]([^'\"]+)['\"]", content)
        down_revision = down_match.group(1) if down_match else None
        
        # Extract date
        date_match = re.search(r"Create Date:\s*([^\n]+)", content)
        create_date = date_match.group(1).strip() if date_match else "?"
        
        migrations.append({
            'file': file.name,
            'revision': revision,
            'down_revision': down_revision,
            'create_date': create_date
        })
    
    # Sort by date if possible
    def sort_key(m):
        try:
            # Try to parse date
            date_str = m['create_date']
            if '2025-10-31' in date_str:
                time_part = date_str.split()[-1] if ' ' in date_str else '00:00:00'
                return datetime(2025, 10, 31, *map(int, time_part.split(':')))
            elif '2025-11-01' in date_str:
                return datetime(2025, 11, 1)
            elif '2025-11-03' in date_str:
                return datetime(2025, 11, 3)
            elif '2025-11-04' in date_str:
                return datetime(2025, 11, 4)
            elif '2025-11-05' in date_str:
                return datetime(2025, 11, 5)
            elif '2025-01-15' in date_str:
                return datetime(2025, 1, 15)
            elif '2025-01-20' in date_str:
                return datetime(2025, 1, 20)
            elif '2025-01-21' in date_str:
                return datetime(2025, 1, 21)
            else:
                return datetime.max
        except:
            return datetime.max
    
    migrations.sort(key=sort_key)
    
    print("=" * 100)
    print("MIGRATION ORDER BY DATE:")
    print("=" * 100)
    for m in migrations:
        print(f"{m['create_date']:30s} | {m['revision']:30s} | -> {m['down_revision'] or 'None':30s} | {m['file']}")
    
    return migrations

if __name__ == "__main__":
    get_migration_info()

