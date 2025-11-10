from typing import Optional, List, Dict, Any
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.role_repository import RoleRepository
from app.schemas.user.request import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPatchRequest,
    UserPasswordUpdateRequest
)
from app.schemas.user.response import UserResponse, UserListResponse
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.core.security import get_password_hash, verify_password
from app.utils.helpers import sanitize_dict


class UserService:
    """Service untuk handle business logic User"""

    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[UserListResponse], int]:
        """Get all users with pagination"""
        from sqlalchemy.orm import joinedload
        from app.models.user.user import User
        
        query = self.db.query(User).options(joinedload(User.role_obj))
        if filters:
            for key, value in filters.items():
                if hasattr(User, key):
                    query = query.filter(getattr(User, key) == value)
        
        users = query.offset(skip).limit(limit).all()
        total = query.count()
        
        result = []
        for user in users:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "role_id": user.role_id,
                "role": {
                    "id": user.role_obj.id,
                    "name": user.role_obj.name,
                    "description": user.role_obj.description
                } if user.role_obj else None,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            result.append(UserListResponse.model_validate(user_dict))
        
        return result, total

    def get_by_id(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        from sqlalchemy.orm import joinedload
        from app.models.user.user import User
        
        user = self.db.query(User).options(joinedload(User.role_obj)).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
        
        user_dict = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "role_id": user.role_id,
            "role": {
                "id": user.role_obj.id,
                "name": user.role_obj.name,
                "description": user.role_obj.description
            } if user.role_obj else None,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        
        return UserResponse.model_validate(user_dict)

    def create(self, user_data: UserCreateRequest) -> UserResponse:
        """Create new user"""
        # Check if email already exists
        if self.repository.email_exists(user_data.email):
            raise ValidationError(f"Email {user_data.email} sudah terdaftar")
        
        # Verify role exists if role_id provided
        if user_data.role_id:
            role = self.role_repo.get(user_data.role_id)
            if not role:
                raise NotFoundError(f"Role dengan ID {user_data.role_id} tidak ditemukan")
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user data dict
        user_dict = {
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": password_hash,
            "role_id": user_data.role_id,
            "is_active": user_data.is_active,
            "is_superuser": user_data.is_superuser,
        }
        
        user = self.repository.create(user_dict)
        if not user:
            raise ValidationError("Gagal membuat user baru")
        
        return self.get_by_id(user.id)

    def update(self, user_id: int, user_data: UserUpdateRequest) -> UserResponse:
        """Update user (full update)"""
        user = self.repository.get(user_id)
        if not user:
            raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
        
        # Check if email changed and already exists
        if user_data.email and user_data.email != user.email:
            if self.repository.email_exists(user_data.email):
                raise ValidationError(f"Email {user_data.email} sudah terdaftar")
        
        # Verify role exists if role_id provided
        if user_data.role_id is not None:
            if user_data.role_id != user.role_id:
                role = self.role_repo.get(user_data.role_id)
                if not role:
                    raise NotFoundError(f"Role dengan ID {user_data.role_id} tidak ditemukan")
        
        # Prepare update data
        update_data = sanitize_dict(user_data.model_dump(exclude_unset=True))
        
        updated_user = self.repository.update(user_id, update_data)
        if not updated_user:
            raise ValidationError("Gagal mengupdate user")
        
        return self.get_by_id(user_id)

    def patch(self, user_id: int, user_data: UserPatchRequest) -> UserResponse:
        """Partial update user"""
        user = self.repository.get(user_id)
        if not user:
            raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
        
        # Check if email changed and already exists
        if user_data.email and user_data.email != user.email:
            if self.repository.email_exists(user_data.email):
                raise ValidationError(f"Email {user_data.email} sudah terdaftar")
        
        # Verify role exists if role_id provided
        if user_data.role_id is not None:
            if user_data.role_id != user.role_id:
                role = self.role_repo.get(user_data.role_id)
                if not role:
                    raise NotFoundError(f"Role dengan ID {user_data.role_id} tidak ditemukan")
        
        # Prepare update data
        update_data = sanitize_dict(user_data.model_dump(exclude_unset=True))
        
        # Handle password update
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        updated_user = self.repository.update(user_id, update_data)
        if not updated_user:
            raise ValidationError("Gagal mengupdate user")
        
        return self.get_by_id(user_id)

    def delete(self, user_id: int) -> bool:
        """Delete user dengan menangani foreign key constraints"""
        logger = logging.getLogger(__name__)
        
        try:
            user = self.repository.get(user_id)
            if not user:
                raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
            
            # Prevent deleting superuser
            if user.is_superuser:
                raise ForbiddenError("Tidak dapat menghapus superuser")
            
            # Cari superuser pertama sebagai fallback untuk foreign key yang tidak nullable
            fallback_user = self.db.query(self.repository.model).filter(
                self.repository.model.is_superuser == True,
                self.repository.model.id != user_id
            ).first()
            
            if not fallback_user:
                # Jika tidak ada superuser lain, cari user aktif pertama
                fallback_user = self.db.query(self.repository.model).filter(
                    self.repository.model.id != user_id,
                    self.repository.model.is_active == True
                ).first()
            
            if not fallback_user:
                raise ValidationError("Tidak dapat menghapus user: tidak ada user lain yang dapat digunakan sebagai fallback")
            
            fallback_user_id = fallback_user.id
            
            logger.info(f"Menghapus user ID {user_id}, menggunakan fallback user ID {fallback_user_id}")
            
            # Update semua foreign key yang merujuk ke user ini
            try:
                # Helper untuk update kolom wajib (harus berhasil agar FK tidak menghalangi delete)
                def update_required(model, filter_expr, update_dict, label: str):
                    try:
                        count_local = self.db.query(model).filter(filter_expr).update(update_dict)
                        logger.info(f"Updated {count_local} {label} records (required)")
                    except Exception as ex:
                        # Jika gagal pada kolom/relasi wajib, bubble up agar ketahuan jelas
                        logger.error(f"Gagal update wajib {label}: {str(ex)}", exc_info=True)
                        raise

                # Helper untuk update kolom opsional (jika kolom tidak ada / mismatch skema, jangan gagalkan proses)
                def update_optional(model, filter_expr, update_dict, label: str):
                    try:
                        self.db.query(model).filter(filter_expr).update(update_dict)
                        logger.info(f"Updated optional {label}")
                    except Exception as ex:
                        logger.warning(f"Lewati optional update {label} karena error: {str(ex)}")

                # Import model-model terkait
                from app.models.inventory.stock_in import StockIn
                from app.models.inventory.stock_out import StockOut
                from app.models.inventory.installed import Installed
                from app.models.inventory.return_model import Return
                from app.models.inventory.surat_permintaan import SuratPermintaan
                from app.models.inventory.surat_jalan import SuratJalan
                from app.models.inventory.audit_log import AuditLog
                from app.models.project.user_project import UserProject
                from app.models.user.user_permission import UserPermission
                from app.models.user.user_menu_preference import UserMenuPreference

                # Kolom wajib: created_by dan audit_logs.user_id
                update_required(StockIn, StockIn.created_by == user_id, {"created_by": fallback_user_id}, "StockIn(created_by)")
                update_optional(StockIn, StockIn.updated_by == user_id, {"updated_by": None}, "StockIn(updated_by)")
                update_optional(StockIn, StockIn.deleted_by == user_id, {"deleted_by": None}, "StockIn(deleted_by)")

                update_required(StockOut, StockOut.created_by == user_id, {"created_by": fallback_user_id}, "StockOut(created_by)")
                update_optional(StockOut, StockOut.updated_by == user_id, {"updated_by": None}, "StockOut(updated_by)")
                update_optional(StockOut, StockOut.deleted_by == user_id, {"deleted_by": None}, "StockOut(deleted_by)")

                update_required(Installed, Installed.created_by == user_id, {"created_by": fallback_user_id}, "Installed(created_by)")
                update_optional(Installed, Installed.updated_by == user_id, {"updated_by": None}, "Installed(updated_by)")
                update_optional(Installed, Installed.deleted_by == user_id, {"deleted_by": None}, "Installed(deleted_by)")

                update_required(Return, Return.created_by == user_id, {"created_by": fallback_user_id}, "Return(created_by)")
                update_optional(Return, Return.updated_by == user_id, {"updated_by": None}, "Return(updated_by)")
                update_optional(Return, Return.deleted_by == user_id, {"deleted_by": None}, "Return(deleted_by)")

                update_required(SuratPermintaan, SuratPermintaan.created_by == user_id, {"created_by": fallback_user_id}, "SuratPermintaan(created_by)")
                update_optional(SuratPermintaan, SuratPermintaan.updated_by == user_id, {"updated_by": None}, "SuratPermintaan(updated_by)")
                update_optional(SuratPermintaan, SuratPermintaan.deleted_by == user_id, {"deleted_by": None}, "SuratPermintaan(deleted_by)")

                update_required(SuratJalan, SuratJalan.created_by == user_id, {"created_by": fallback_user_id}, "SuratJalan(created_by)")
                update_optional(SuratJalan, SuratJalan.updated_by == user_id, {"updated_by": None}, "SuratJalan(updated_by)")
                update_optional(SuratJalan, SuratJalan.deleted_by == user_id, {"deleted_by": None}, "SuratJalan(deleted_by)")

                # AuditLog (wajib)
                update_required(AuditLog, AuditLog.user_id == user_id, {"user_id": fallback_user_id}, "AuditLog(user_id)")

                # Tabel relasi (hapus baris, aman jika kosong)
                try:
                    count_up = self.db.query(UserProject).filter(UserProject.user_id == user_id).delete()
                    logger.info(f"Deleted {count_up} UserProject records")
                except Exception as ex:
                    logger.warning(f"Lewati delete UserProject karena error: {str(ex)}")

                try:
                    count_perm = self.db.query(UserPermission).filter(UserPermission.user_id == user_id).delete()
                    logger.info(f"Deleted {count_perm} UserPermission records")
                except Exception as ex:
                    logger.warning(f"Lewati delete UserPermission karena error: {str(ex)}")

                try:
                    count_pref = self.db.query(UserMenuPreference).filter(UserMenuPreference.user_id == user_id).delete()
                    logger.info(f"Deleted {count_pref} UserMenuPreference records")
                except Exception as ex:
                    logger.warning(f"Lewati delete UserMenuPreference karena error: {str(ex)}")

                # Commit perubahan foreign key
                self.db.commit()
                logger.info(f"Foreign key constraints berhasil diupdate untuk user ID {user_id}")

            except Exception as e:
                self.db.rollback()
                logger.error(f"Error saat update foreign key untuk user ID {user_id}: {str(e)}", exc_info=True)
                raise
            
            # Sekarang baru hapus user (repository.delete sudah commit sendiri)
            try:
                result = self.repository.delete(user_id)
                if not result:
                    raise ValidationError("Gagal menghapus user")
                logger.info(f"User ID {user_id} berhasil dihapus")
            except Exception as e:
                logger.error(f"Error saat delete user ID {user_id}: {str(e)}", exc_info=True)
                raise
            
            return True
            
        except (NotFoundError, ForbiddenError, ValidationError):
            # Re-raise custom exceptions
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error saat menghapus user ID {user_id}: {str(e)}", exc_info=True)
            raise ValidationError(f"Gagal menghapus user: terdapat constraint database yang dilanggar. Detail: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error saat menghapus user ID {user_id}: {str(e)}", exc_info=True)
            raise ValidationError(f"Gagal menghapus user: terjadi kesalahan pada database. Detail: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error saat menghapus user ID {user_id}: {str(e)}", exc_info=True)
            raise ValidationError(f"Gagal menghapus user: {str(e)}")

    def update_password(
        self,
        user_id: int,
        password_data: UserPasswordUpdateRequest
    ) -> bool:
        """Update user password"""
        user = self.repository.get(user_id)
        if not user:
            raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
        
        # Verify old password
        if not verify_password(password_data.old_password, user.password_hash):
            raise ValidationError("Password lama tidak sesuai")
        
        # Update password
        new_password_hash = get_password_hash(password_data.new_password)
        updated_user = self.repository.update(user_id, {"password_hash": new_password_hash})
        
        if not updated_user:
            raise ValidationError("Gagal mengupdate password")
        
        return True

