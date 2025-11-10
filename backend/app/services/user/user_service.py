from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
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
        
        # Update semua foreign key yang merujuk ke user ini
        # StockIn
        from app.models.inventory.stock_in import StockIn
        self.db.query(StockIn).filter(StockIn.created_by == user_id).update({"created_by": fallback_user_id})
        self.db.query(StockIn).filter(StockIn.updated_by == user_id).update({"updated_by": None})
        self.db.query(StockIn).filter(StockIn.deleted_by == user_id).update({"deleted_by": None})
        
        # StockOut
        from app.models.inventory.stock_out import StockOut
        self.db.query(StockOut).filter(StockOut.created_by == user_id).update({"created_by": fallback_user_id})
        self.db.query(StockOut).filter(StockOut.updated_by == user_id).update({"updated_by": None})
        self.db.query(StockOut).filter(StockOut.deleted_by == user_id).update({"deleted_by": None})
        
        # Installed
        from app.models.inventory.installed import Installed
        self.db.query(Installed).filter(Installed.created_by == user_id).update({"created_by": fallback_user_id})
        self.db.query(Installed).filter(Installed.updated_by == user_id).update({"updated_by": None})
        self.db.query(Installed).filter(Installed.deleted_by == user_id).update({"deleted_by": None})
        
        # Return
        from app.models.inventory.return_model import Return
        self.db.query(Return).filter(Return.created_by == user_id).update({"created_by": fallback_user_id})
        self.db.query(Return).filter(Return.updated_by == user_id).update({"updated_by": None})
        self.db.query(Return).filter(Return.deleted_by == user_id).update({"deleted_by": None})
        
        # SuratPermintaan
        from app.models.inventory.surat_permintaan import SuratPermintaan
        self.db.query(SuratPermintaan).filter(SuratPermintaan.created_by == user_id).update({"created_by": fallback_user_id})
        self.db.query(SuratPermintaan).filter(SuratPermintaan.updated_by == user_id).update({"updated_by": None})
        self.db.query(SuratPermintaan).filter(SuratPermintaan.deleted_by == user_id).update({"deleted_by": None})
        
        # SuratJalan
        from app.models.inventory.surat_jalan import SuratJalan
        self.db.query(SuratJalan).filter(SuratJalan.created_by == user_id).update({"created_by": fallback_user_id})
        self.db.query(SuratJalan).filter(SuratJalan.updated_by == user_id).update({"updated_by": None})
        self.db.query(SuratJalan).filter(SuratJalan.deleted_by == user_id).update({"deleted_by": None})
        
        # AuditLog
        from app.models.inventory.audit_log import AuditLog
        self.db.query(AuditLog).filter(AuditLog.user_id == user_id).update({"user_id": fallback_user_id})
        
        # Commit perubahan foreign key
        self.db.commit()
        
        # Sekarang baru hapus user
        result = self.repository.delete(user_id)
        if not result:
            raise ValidationError("Gagal menghapus user")
        
        return True

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

