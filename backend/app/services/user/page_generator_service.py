"""
Service untuk auto-generate pages dan permissions dari configuration.
"""
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.repositories.user.permission_repository import PageRepository, PermissionRepository
from app.models.user.permission import Page, Permission
import logging

logger = logging.getLogger(__name__)


class PageGeneratorService:
    """Service untuk handle auto-generate pages dan permissions"""

    def __init__(self, db: Session):
        self.db = db
        self.page_repo = PageRepository(db)
        self.permission_repo = PermissionRepository(db)

    def upsert_page(self, page_data: Dict) -> Page:
        """
        Upsert page berdasarkan path.
        - Jika path sudah ada: update hanya icon dan order (jika display_name belum di-custom)
        - Jika display_name berbeda dari config, skip update (user sudah custom)
        - Jika path belum ada: create baru
        """
        existing = self.page_repo.get_by_path(page_data['path'])

        if existing:
            # Check jika display_name sudah di-custom (berbeda dari config)
            if existing.display_name != page_data['display_name']:
                # Skip update, user sudah custom display_name
                logger.debug(
                    f"Page {page_data['path']} sudah ada dengan display_name custom, skip update"
                )
                return existing

            # Update hanya icon dan order (metadata non-kritis)
            update_data = {}
            if page_data.get('icon'):
                update_data['icon'] = page_data['icon']
            if page_data.get('order') is not None:
                update_data['order'] = page_data['order']

            if update_data:
                updated = self.page_repo.update(existing.id, update_data)
                logger.debug(f"Page {page_data['path']} updated: {update_data}")
                return updated
            return existing
        else:
            # Create baru
            created = self.page_repo.create(page_data)
            logger.info(f"Page baru created: {page_data['path']} - {page_data['display_name']}")
            return created

    def ensure_default_permission(self, page_id: int) -> Permission:
        """
        Ensure default permission untuk page.
        - Buat permission default dengan semua CRUD = False (secure by default)
        - Skip jika sudah ada permission untuk page ini
        """
        existing = self.permission_repo.get_by_page_id(page_id)

        if existing:
            # Sudah ada permission, return yang pertama
            logger.debug(f"Permission untuk page_id {page_id} sudah ada, skip create")
            return existing[0]

        # Create default permission dengan semua CRUD = False
        permission_data = {
            'page_id': page_id,
            'can_create': False,
            'can_read': False,
            'can_update': False,
            'can_delete': False,
        }
        created = self.permission_repo.create(permission_data)
        logger.info(f"Permission default created untuk page_id {page_id}")
        return created

    def generate_pages_from_config(self, pages_config: List[Dict]) -> Dict[str, int]:
        """
        Generate pages dari configuration.
        
        Args:
            pages_config: List of dict dengan keys: name, path, display_name, icon, order
            
        Returns:
            Dict dengan stats: {'created': int, 'updated': int, 'skipped': int}
        """
        stats = {'created': 0, 'updated': 0, 'skipped': 0}

        try:
            for page_data in pages_config:
                # Validate required fields
                if not all(key in page_data for key in ['name', 'path', 'display_name']):
                    logger.warning(f"Page config tidak lengkap: {page_data}, skip")
                    continue

                # Check existing
                existing = self.page_repo.get_by_path(page_data['path'])
                was_existing = existing is not None

                # Upsert page
                page = self.upsert_page(page_data)
                
                if not was_existing:
                    stats['created'] += 1
                elif existing and existing.display_name == page_data['display_name']:
                    stats['updated'] += 1
                else:
                    stats['skipped'] += 1

                # Ensure default permission
                self.ensure_default_permission(page.id)

            self.db.commit()
            logger.info(
                f"Pages generation completed: "
                f"{stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped"
            )
            return stats

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating pages: {str(e)}", exc_info=True)
            raise

