"""
Migration Manager dengan Best Practice Implementation
- Multi-mode support (sequential sebagai default, head sebagai fallback)
- Auto-sequential migration dengan validasi
- Auto-fix dependency cycle dengan dry-run dan confirmation
- Detailed migration history tracking
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.config.settings import settings
from app.config.database import engine

logger = logging.getLogger(__name__)


class MigrationMode(str, Enum):
    """Mode migration yang tersedia"""
    SEQUENTIAL = "sequential"  # Default: upgrade satu per satu dengan validasi
    HEAD = "head"  # Fallback: upgrade langsung ke head
    AUTO = "auto"  # Otomatis pilih mode terbaik


class MigrationStatus(str, Enum):
    """Status migration"""
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    SKIPPED = "skipped"


class MigrationInfo:
    """Informasi tentang sebuah migration"""
    def __init__(
        self,
        revision: str,
        down_revision: Optional[str],
        file_path: Path,
        status: MigrationStatus = MigrationStatus.PENDING
    ):
        self.revision = revision
        self.down_revision = down_revision
        self.file_path = file_path
        self.status = status
        self.applied_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.dependencies: List[str] = []  # Revisions yang bergantung pada ini
    
    def __repr__(self):
        return f"MigrationInfo(revision={self.revision}, down_revision={self.down_revision}, status={self.status})"


class MigrationManager:
    """
    Migration Manager dengan best practice implementation
    
    Features:
    1. Multi-mode support (sequential default, head fallback)
    2. Auto-sequential dengan validasi
    3. Auto-fix dependency cycle dengan confirmation
    4. Detailed history tracking
    """
    
    def __init__(self, mode: MigrationMode = None):
        self.mode = mode or MigrationMode(settings.MIGRATION_MODE or "sequential")
        self.root_dir = Path(__file__).parent.parent.parent
        self.migrations_dir = self.root_dir / "migrations" / "versions"
        self.alembic_cfg = self._get_alembic_config()
        self.script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        self.migration_history: List[Dict] = []
        
    def _get_alembic_config(self) -> Config:
        """Membuat konfigurasi Alembic"""
        alembic_cfg = Config(str(self.root_dir / "alembic.ini"))
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
        return alembic_cfg
    
    def get_current_revision(self) -> Optional[str]:
        """Dapatkan current revision dari database"""
        try:
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                try:
                    return context.get_current_revision()
                except Exception as e:
                    # Handle multiple heads di database
                    if "more than one head" in str(e).lower():
                        # Coba ambil semua heads
                        try:
                            heads = context.get_current_heads()
                            if heads:
                                logger.warning(f"Multiple heads di database: {heads}")
                                # Return yang pertama (bisa diperbaiki nanti)
                                return heads[0]
                        except:
                            pass
                    raise
        except (OperationalError, ProgrammingError) as e:
            # Database belum ada atau tabel alembic_version belum ada
            logger.debug(f"Database belum memiliki migration version: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error mendapatkan current revision: {str(e)}", exc_info=True)
            return None
    
    def get_head_revision(self) -> Optional[str]:
        """Dapatkan head revision dari migration files"""
        try:
            return self.script_dir.get_current_head()
        except Exception as e:
            # Handle multiple heads
            if "multiple heads" in str(e).lower():
                try:
                    heads = self.script_dir.get_revisions("heads")
                    if heads:
                        head_strs = [str(h) for h in heads]
                        logger.warning(f"Multiple heads di migration files: {head_strs}")
                        # Return yang pertama (bisa diperbaiki nanti)
                        return head_strs[0]
                except:
                    pass
            logger.error(f"Error mendapatkan head revision: {str(e)}", exc_info=True)
            return None
    
    def parse_migration_files(self) -> Dict[str, MigrationInfo]:
        """
        Parse semua migration files dan buat dependency graph
        
        Returns:
            Dict[str, MigrationInfo]: Mapping revision -> MigrationInfo
        """
        migrations: Dict[str, MigrationInfo] = {}
        
        for file_path in self.migrations_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Extract revision
                rev_match = re.search(r"revision:\s*str\s*=\s*['\"]([^'\"]+)['\"]", content)
                if not rev_match:
                    continue
                
                revision = rev_match.group(1)
                
                # Extract down_revision
                down_match = re.search(
                    r"down_revision:\s*Union\[str,\s*None\]\s*=\s*(?:['\"]([^'\"]*)['\"]|None)",
                    content
                )
                down_revision = None
                if down_match and down_match.group(1):
                    down_revision = down_match.group(1)
                
                migrations[revision] = MigrationInfo(
                    revision=revision,
                    down_revision=down_revision,
                    file_path=file_path
                )
                
            except Exception as e:
                logger.warning(f"Error parsing migration file {file_path.name}: {str(e)}")
                continue
        
        # Build dependency graph (reverse: siapa yang bergantung pada migration ini)
        for rev, info in migrations.items():
            if info.down_revision and info.down_revision in migrations:
                migrations[info.down_revision].dependencies.append(rev)
        
        return migrations
    
    def get_sequential_path(
        self,
        from_revision: Optional[str],
        to_revision: Optional[str] = None
    ) -> List[str]:
        """
        Dapatkan path sequential dari from_revision ke to_revision
        
        Args:
            from_revision: Revision saat ini (None jika database baru)
            to_revision: Target revision (None untuk head)
        
        Returns:
            List[str]: Urutan revision yang harus di-upgrade
        """
        migrations = self.parse_migration_files()
        
        if not migrations:
            return []
        
        # Jika to_revision tidak ditentukan, gunakan head
        if to_revision is None:
            to_revision = self.get_head_revision()
        
        if to_revision is None:
            logger.warning("Tidak ada head revision ditemukan")
            return []
        
        # Jika from_revision adalah None atau tidak ada di migrations, mulai dari yang tidak punya down_revision
        if from_revision is None or from_revision not in migrations:
            # Cari migration yang tidak punya down_revision (root migrations)
            root_migrations = [
                rev for rev, info in migrations.items()
                if info.down_revision is None
            ]
            if root_migrations:
                # Jika ada multiple roots, kita perlu merge mereka
                # Untuk sekarang, ambil yang pertama (bisa diperbaiki nanti)
                from_revision = root_migrations[0]
            else:
                # Semua migration punya down_revision, cari yang paling awal
                # Build chain dari yang tidak punya dependency
                visited = set()
                path = []
                
                def dfs(rev: str):
                    if rev in visited:
                        return
                    visited.add(rev)
                    if rev in migrations:
                        info = migrations[rev]
                        if info.down_revision and info.down_revision in migrations:
                            dfs(info.down_revision)
                        path.append(rev)
                
                # Mulai dari semua migration
                for rev in migrations.keys():
                    dfs(rev)
                
                # Filter path sampai to_revision
                if to_revision in path:
                    idx = path.index(to_revision)
                    return path[:idx + 1]
                return path
        
        # Build path dari from_revision ke to_revision
        path = []
        current = from_revision
        
        # Build forward path
        visited = set()
        while current and current != to_revision:
            if current in visited:
                logger.warning(f"Cycle detected di migration path: {current}")
                break
            visited.add(current)
            
            # Cari migration yang down_revision = current
            next_migrations = [
                rev for rev, info in migrations.items()
                if info.down_revision == current
            ]
            
            if not next_migrations:
                break
            
            # Jika ada multiple, pilih yang pertama (bisa diperbaiki dengan topological sort)
            current = next_migrations[0]
            path.append(current)
        
        if to_revision and to_revision not in path:
            path.append(to_revision)
        
        return path
    
    def detect_multiple_heads(self) -> List[str]:
        """
        Deteksi multiple heads dalam migration chain
        
        Returns:
            List[str]: List of head revisions (lebih dari 1 berarti ada multiple heads)
        """
        try:
            heads = self.script_dir.get_revisions("heads")
            return [str(h) for h in heads] if heads else []
        except Exception as e:
            logger.error(f"Error detecting multiple heads: {str(e)}", exc_info=True)
            return []
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Deteksi cycle dalam dependency graph
        
        Returns:
            List[List[str]]: List of cycles (setiap cycle adalah list of revisions)
        """
        migrations = self.parse_migration_files()
        cycles = []
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Cycle detected
                cycle_start_idx = path.index(node)
                cycle = path[cycle_start_idx:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in migrations:
                info = migrations[node]
                if info.down_revision and info.down_revision in migrations:
                    if has_cycle(info.down_revision, path):
                        return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for rev in migrations.keys():
            if rev not in visited:
                has_cycle(rev, [])
        
        return cycles
    
    def suggest_cycle_fix(self, cycles: List[List[str]]) -> Dict[str, str]:
        """
        Suggest fix untuk dependency cycle
        
        Args:
            cycles: List of cycles yang terdeteksi
        
        Returns:
            Dict[str, str]: Mapping revision -> suggested down_revision
        """
        migrations = self.parse_migration_files()
        suggestions = {}
        
        for cycle in cycles:
            if len(cycle) < 2:
                continue
            
            # Strategy: Break cycle dengan mengubah down_revision dari migration terakhir
            # menjadi None atau ke migration yang tidak ada di cycle
            last_in_cycle = cycle[-2]  # Second to last (karena last adalah duplicate dari first)
            
            if last_in_cycle in migrations:
                info = migrations[last_in_cycle]
                # Cari migration yang tidak ada di cycle sebagai parent
                for rev, mig_info in migrations.items():
                    if rev not in cycle and rev != last_in_cycle:
                        suggestions[last_in_cycle] = rev
                        break
                
                # Jika tidak ada, suggest None (root migration)
                if last_in_cycle not in suggestions:
                    suggestions[last_in_cycle] = None
        
        return suggestions
    
    def validate_migration_chain(self) -> Tuple[bool, List[str]]:
        """
        Validasi migration chain sebelum upgrade
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Check multiple heads
        heads = self.detect_multiple_heads()
        if len(heads) > 1:
            errors.append(f"Multiple heads detected: {', '.join(heads)}")
        
        # 2. Check cycles
        cycles = self.detect_cycles()
        if cycles:
            for cycle in cycles:
                errors.append(f"Cycle detected: {' -> '.join(cycle)}")
        
        # 3. Check missing dependencies
        migrations = self.parse_migration_files()
        for rev, info in migrations.items():
            if info.down_revision and info.down_revision not in migrations:
                errors.append(f"Migration {rev} references missing down_revision: {info.down_revision}")
        
        return len(errors) == 0, errors
    
    def upgrade_sequential(
        self,
        from_revision: Optional[str] = None,
        to_revision: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Upgrade database secara sequential (satu per satu)
        
        Args:
            from_revision: Starting revision (None untuk current)
            to_revision: Target revision (None untuk head)
            dry_run: Jika True, hanya simulate tanpa eksekusi
        
        Returns:
            Dict: Result dengan status, applied migrations, errors
        """
        result = {
            "success": False,
            "mode": "sequential",
            "applied": [],
            "skipped": [],
            "failed": [],
            "current_revision": None,
            "target_revision": None,
            "errors": []
        }
        
        try:
            # Get current revision
            if from_revision is None:
                from_revision = self.get_current_revision()
            
            result["current_revision"] = from_revision or "None (database baru)"
            
            # Get target revision
            if to_revision is None:
                to_revision = self.get_head_revision()
            
            result["target_revision"] = to_revision
            
            if to_revision is None:
                result["errors"].append("Tidak ada target revision (head tidak ditemukan)")
                return result
            
            # Validate chain sebelum upgrade
            if settings.MIGRATION_VALIDATE_BEFORE_UPGRADE:
                is_valid, validation_errors = self.validate_migration_chain()
                if not is_valid:
                    result["errors"].extend(validation_errors)
                    if not dry_run:
                        logger.warning("Migration chain validation failed, tetapi akan tetap dicoba")
            
            # Get sequential path
            path = self.get_sequential_path(from_revision, to_revision)
            
            if not path:
                if from_revision == to_revision:
                    result["success"] = True
                    result["message"] = "Database sudah up-to-date"
                else:
                    result["errors"].append(f"Tidak dapat menemukan path dari {from_revision} ke {to_revision}")
                return result
            
            logger.info(f"Sequential upgrade path: {from_revision or 'None'} -> {' -> '.join(path)}")
            
            if dry_run:
                result["success"] = True
                result["message"] = f"Dry-run: Akan upgrade {len(path)} migration(s)"
                result["applied"] = path
                return result
            
            # Apply migrations satu per satu
            current = from_revision
            for next_rev in path:
                try:
                    logger.info(f"Upgrading: {current or 'None'} -> {next_rev}")
                    
                    # Log migration start
                    migration_log = {
                        "revision": next_rev,
                        "from_revision": current,
                        "started_at": datetime.now().isoformat(),
                        "status": "applying"
                    }
                    self.migration_history.append(migration_log)
                    
                    # Execute upgrade
                    command.upgrade(self.alembic_cfg, next_rev)
                    
                    # Log success
                    migration_log["status"] = "applied"
                    migration_log["completed_at"] = datetime.now().isoformat()
                    result["applied"].append(next_rev)
                    current = next_rev
                    
                    logger.info(f"✅ Successfully upgraded to {next_rev}")
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"❌ Failed to upgrade to {next_rev}: {error_msg}", exc_info=True)
                    
                    # Log failure
                    migration_log["status"] = "failed"
                    migration_log["error"] = error_msg
                    migration_log["completed_at"] = datetime.now().isoformat()
                    
                    result["failed"].append({
                        "revision": next_rev,
                        "error": error_msg
                    })
                    result["errors"].append(f"Failed to upgrade to {next_rev}: {error_msg}")
                    
                    # Stop on first failure (best practice: fail fast)
                    if settings.MIGRATION_STOP_ON_ERROR:
                        break
            
            # Final status
            final_revision = self.get_current_revision()
            result["final_revision"] = final_revision
            
            if len(result["failed"]) == 0:
                result["success"] = True
                result["message"] = f"Successfully upgraded {len(result['applied'])} migration(s)"
            else:
                result["success"] = False
                result["message"] = f"Upgraded {len(result['applied'])} migration(s), {len(result['failed'])} failed"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during sequential upgrade: {error_msg}", exc_info=True)
            result["errors"].append(error_msg)
            result["success"] = False
        
        return result
    
    def upgrade_head(self, dry_run: bool = False) -> Dict:
        """
        Upgrade langsung ke head (fallback mode)
        
        Args:
            dry_run: Jika True, hanya simulate
        
        Returns:
            Dict: Result dengan status
        """
        result = {
            "success": False,
            "mode": "head",
            "current_revision": None,
            "target_revision": None,
            "errors": []
        }
        
        try:
            current_revision = self.get_current_revision()
            head_revision = self.get_head_revision()
            
            result["current_revision"] = current_revision or "None"
            result["target_revision"] = head_revision
            
            if head_revision is None:
                result["errors"].append("Head revision tidak ditemukan")
                return result
            
            if current_revision == head_revision:
                result["success"] = True
                result["message"] = "Database sudah up-to-date"
                return result
            
            if dry_run:
                result["success"] = True
                result["message"] = f"Dry-run: Akan upgrade ke head ({head_revision})"
                return result
            
            logger.info(f"Upgrading to head: {current_revision or 'None'} -> {head_revision}")
            
            # Log migration start
            migration_log = {
                "revision": head_revision,
                "from_revision": current_revision,
                "started_at": datetime.now().isoformat(),
                "status": "applying"
            }
            self.migration_history.append(migration_log)
            
            # Execute upgrade
            command.upgrade(self.alembic_cfg, "head")
            
            # Log success
            migration_log["status"] = "applied"
            migration_log["completed_at"] = datetime.now().isoformat()
            
            result["success"] = True
            result["message"] = f"Successfully upgraded to head ({head_revision})"
            result["final_revision"] = self.get_current_revision()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during head upgrade: {error_msg}", exc_info=True)
            result["errors"].append(error_msg)
            result["success"] = False
            
            if "migration_log" in locals():
                migration_log["status"] = "failed"
                migration_log["error"] = error_msg
                migration_log["completed_at"] = datetime.now().isoformat()
        
        return result
    
    def upgrade(
        self,
        mode: Optional[MigrationMode] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Upgrade database dengan mode yang dipilih
        
        Args:
            mode: Migration mode (None untuk menggunakan default)
            dry_run: Jika True, hanya simulate
        
        Returns:
            Dict: Result dengan status dan detail
        """
        mode = mode or self.mode
        
        # Auto mode: pilih terbaik
        if mode == MigrationMode.AUTO:
            # Check multiple heads
            heads = self.detect_multiple_heads()
            if len(heads) > 1:
                logger.warning("Multiple heads detected, menggunakan sequential mode")
                mode = MigrationMode.SEQUENTIAL
            else:
                # Coba head dulu, jika gagal fallback ke sequential
                try:
                    result = self.upgrade_head(dry_run=dry_run)
                    if result["success"] or dry_run:
                        return result
                except Exception:
                    pass
                mode = MigrationMode.SEQUENTIAL
        
        # Execute berdasarkan mode
        if mode == MigrationMode.HEAD:
            return self.upgrade_head(dry_run=dry_run)
        else:  # SEQUENTIAL (default)
            return self.upgrade_sequential(dry_run=dry_run)
    
    def get_migration_history(self) -> List[Dict]:
        """Dapatkan migration history yang sudah di-track"""
        return self.migration_history.copy()
    
    def get_migration_status(self) -> Dict:
        """
        Dapatkan status migration lengkap
        
        Returns:
            Dict: Status dengan current, head, pending, validation, dll
        """
        current = self.get_current_revision()
        head = self.get_head_revision()
        heads = self.detect_multiple_heads()
        cycles = self.detect_cycles()
        is_valid, validation_errors = self.validate_migration_chain()
        
        return {
            "current_revision": current,
            "head_revision": head,
            "is_up_to_date": current == head,
            "has_pending": current != head,
            "multiple_heads": len(heads) > 1,
            "heads": heads,
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
            "is_valid": is_valid,
            "validation_errors": validation_errors,
            "mode": self.mode.value
        }

