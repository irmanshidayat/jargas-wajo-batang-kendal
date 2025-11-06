"""
Script untuk assign data existing ke default project
Run ini setelah migration add_project_multi_tenant selesai
"""
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.project.project import Project
from app.models.user.user import User
from app.models.inventory.material import Material
from app.models.inventory.mandor import Mandor
from app.models.inventory.stock_in import StockIn
from app.models.inventory.stock_out import StockOut
from app.models.inventory.installed import Installed
from app.models.inventory.return_model import Return
from app.models.inventory.audit_log import AuditLog

def migrate_data_to_default_project():
    """Assign semua data existing ke default project"""
    db = next(get_db())
    
    try:
        # Buat default project jika belum ada
        default_project = db.query(Project).filter(Project.code == "DEFAULT").first()
        if not default_project:
            default_project = Project(
                name="Default Project",
                code="DEFAULT",
                description="Project default untuk data existing",
                is_active=True
            )
            db.add(default_project)
            db.commit()
            db.refresh(default_project)
            print(f"Default project created dengan ID: {default_project.id}")
        else:
            print(f"Default project sudah ada dengan ID: {default_project.id}")
        
        project_id = default_project.id
        
        # Update materials yang belum punya project_id
        materials_updated = db.query(Material).filter(Material.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {materials_updated} materials")
        
        # Update mandors yang belum punya project_id
        mandors_updated = db.query(Mandor).filter(Mandor.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {mandors_updated} mandors")
        
        # Update stock_ins yang belum punya project_id
        stock_ins_updated = db.query(StockIn).filter(StockIn.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {stock_ins_updated} stock_ins")
        
        # Update stock_outs yang belum punya project_id
        stock_outs_updated = db.query(StockOut).filter(StockOut.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {stock_outs_updated} stock_outs")
        
        # Update installed yang belum punya project_id
        installed_updated = db.query(Installed).filter(Installed.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {installed_updated} installed items")
        
        # Update returns yang belum punya project_id
        returns_updated = db.query(Return).filter(Return.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {returns_updated} returns")
        
        # Update audit_logs yang belum punya project_id
        audit_logs_updated = db.query(AuditLog).filter(AuditLog.project_id.is_(None)).update(
            {"project_id": project_id}, synchronize_session=False
        )
        db.commit()
        print(f"Updated {audit_logs_updated} audit logs")
        
        # Assign semua user ke default project sebagai owner (jika belum ada)
        users = db.query(User).all()
        from app.models.project.user_project import UserProject
        
        for user in users:
            existing = db.query(UserProject).filter(
                UserProject.user_id == user.id,
                UserProject.project_id == project_id
            ).first()
            
            if not existing:
                user_project = UserProject(
                    user_id=user.id,
                    project_id=project_id,
                    is_active=True,
                    is_owner=True
                )
                db.add(user_project)
                print(f"Assigned user {user.email} to default project as owner")
        
        db.commit()
        print("\nMigration selesai! Semua data existing telah di-assign ke default project.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data_to_default_project()

