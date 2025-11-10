"""Script untuk menganalisis dependency chain migration Alembic"""
import os
import re
from pathlib import Path

def analyze_migrations():
    """Analisis semua migration dan dependency chain"""
    migrations_dir = Path(__file__).parent.parent / "migrations" / "versions"
    
    deps = {}
    rev_to_file = {}
    
    for file in migrations_dir.glob("*.py"):
        content = file.read_text(encoding='utf-8')
        
        # Extract revision
        rev_match = re.search(r"revision:\s*str\s*=\s*['\"]([^'\"]+)['\"]", content)
        if not rev_match:
            continue
            
        revision = rev_match.group(1)
        rev_to_file[revision] = file.name
        
        # Extract down_revision
        down_match = re.search(r"down_revision:\s*Union\[str,\s*None\]\s*=\s*['\"]([^'\"]+)['\"]", content)
        if down_match:
            down_revision = down_match.group(1)
            deps[revision] = down_revision
        else:
            deps[revision] = None
    
    print("=" * 80)
    print("DEPENDENCY CHAIN:")
    print("=" * 80)
    for rev, down in sorted(deps.items()):
        if down:
            print(f"{rev:30s} -> {down:30s} ({rev_to_file.get(rev, '?')})")
        else:
            print(f"{rev:30s} -> None ({rev_to_file.get(rev, '?')})")
    
    print("\n" + "=" * 80)
    print("CHECKING FOR CYCLES:")
    print("=" * 80)
    
    # Check for cycles
    visited = set()
    rec_stack = set()
    cycles = []
    
    def has_cycle(node):
        if node in rec_stack:
            cycle_start = node
            cycle = [cycle_start]
            current = deps.get(cycle_start)
            while current and current != cycle_start:
                cycle.append(current)
                current = deps.get(current)
                if len(cycle) > 20:  # Prevent infinite loop
                    break
            cycles.append(cycle)
            return True
        
        if node in visited:
            return False
        
        visited.add(node)
        rec_stack.add(node)
        
        if node in deps and deps[node]:
            if has_cycle(deps[node]):
                return True
        
        rec_stack.remove(node)
        return False
    
    for rev in deps.keys():
        if rev not in visited:
            has_cycle(rev)
    
    if cycles:
        print("CYCLES DETECTED:")
        for cycle in cycles:
            print(f"  {' -> '.join(cycle)} -> {cycle[0]}")
    else:
        print("No cycles detected!")
    
    return deps, cycles

if __name__ == "__main__":
    analyze_migrations()



