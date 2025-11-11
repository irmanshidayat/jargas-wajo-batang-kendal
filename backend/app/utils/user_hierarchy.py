from typing import List, Set
from sqlalchemy.orm import Session
from app.models.user.user import User


def get_parent_user_id(db: Session, user_id: int) -> int | None:
    """
    Mendapatkan parent user ID (user yang membuat user ini)
    
    Args:
        db: Database session
        user_id: ID user yang ingin dicari parent-nya
        
    Returns:
        Parent user ID atau None jika tidak ada
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.created_by:
        return user.created_by
    return None


def get_child_user_ids(db: Session, user_id: int, recursive: bool = True) -> List[int]:
    """
    Mendapatkan semua child user IDs (users yang dibuat oleh user ini)
    
    Args:
        db: Database session
        user_id: ID user yang ingin dicari child-nya
        recursive: Jika True, akan mencari child secara recursive (semua descendant)
        
    Returns:
        List of child user IDs
    """
    child_ids: List[int] = []
    
    # Get direct children
    direct_children = db.query(User).filter(User.created_by == user_id).all()
    for child in direct_children:
        child_ids.append(child.id)
        
        # If recursive, get children of children
        if recursive:
            grand_children = get_child_user_ids(db, child.id, recursive=True)
            child_ids.extend(grand_children)
    
    return child_ids


def get_user_hierarchy_ids(db: Session, user_id: int) -> List[int]:
    """
    Mendapatkan semua user IDs yang bisa diakses oleh user ini
    (self + parent + all children recursive)
    
    Args:
        db: Database session
        user_id: ID user yang ingin dicari hierarchy-nya
        
    Returns:
        List of user IDs yang bisa diakses (termasuk user_id sendiri)
    """
    user_ids: Set[int] = {user_id}  # Include self
    
    # Get parent user ID
    parent_id = get_parent_user_id(db, user_id)
    if parent_id:
        user_ids.add(parent_id)
    
    # Get all child user IDs (recursive)
    child_ids = get_child_user_ids(db, user_id, recursive=True)
    user_ids.update(child_ids)
    
    return list(user_ids)


def filter_by_user_hierarchy(query, db: Session, user_id: int, created_by_column):
    """
    Filter query berdasarkan user hierarchy
    User dapat mengakses data yang dibuat oleh:
    - Dirinya sendiri
    - Parent user (user yang membuatnya)
    - Semua child users (users yang dibuat oleh user tersebut, recursive)
    
    Args:
        query: SQLAlchemy query object
        db: Database session
        user_id: ID user yang sedang mengakses
        created_by_column: Column reference untuk created_by (e.g., Model.created_by)
        
    Returns:
        Filtered query
    """
    from sqlalchemy import or_
    
    # Get all user IDs that can be accessed
    accessible_user_ids = get_user_hierarchy_ids(db, user_id)
    
    if not accessible_user_ids:
        # If no accessible users, return empty result
        return query.filter(False)
    
    # Filter by created_by in accessible user IDs
    return query.filter(created_by_column.in_(accessible_user_ids))

