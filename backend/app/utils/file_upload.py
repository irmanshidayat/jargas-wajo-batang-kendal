import os
import uuid
from datetime import date
from typing import List
from fastapi import UploadFile
from pathlib import Path
from PIL import Image
import json


# Base upload directory
UPLOAD_DIR = Path("uploads/evidence")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

# Max file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_uploaded_files(
    files: List[UploadFile],
    evidence_type: str,  # stock_in, stock_out, installed, return
    record_id: int
) -> List[str]:
    """
    Save multiple uploaded files dan return list of file paths
    evidence_type: stock_in, stock_out, installed, return
    """
    saved_paths = []
    today = date.today()
    
    # Create directory structure: uploads/evidence/{type}/YYYY/MM/
    save_dir = UPLOAD_DIR / evidence_type / str(today.year) / f"{today.month:02d}"
    save_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        if file.filename:
            # Validate file type
            if file.content_type not in ALLOWED_TYPES:
                continue
            
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            unique_filename = f"evidence_{evidence_type}_{record_id}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = save_dir / unique_filename
            
            # Read file content
            content = await file.read()
            
            # Validate file size
            if len(content) > MAX_FILE_SIZE:
                continue
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Compress image if it's an image
            if file.content_type in ALLOWED_IMAGE_TYPES:
                try:
                    img = Image.open(file_path)
                    # Convert to RGB if necessary
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    # Resize if too large (max 1920x1080)
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    img.save(file_path, "JPEG", quality=85, optimize=True)
                except Exception:
                    pass  # Skip compression if fails
            
            # Save relative path
            relative_path = f"evidence/{evidence_type}/{today.year}/{today.month:02d}/{unique_filename}"
            saved_paths.append(relative_path)
    
    return saved_paths


def save_evidence_paths_to_db(evidence_paths: List[str]) -> str:
    """Convert list of paths to JSON string for database storage"""
    return json.dumps(evidence_paths, ensure_ascii=False)


def get_evidence_paths_from_db(evidence_paths_json: str) -> List[str]:
    """Convert JSON string from database to list of paths"""
    if not evidence_paths_json:
        return []
    try:
        return json.loads(evidence_paths_json)
    except json.JSONDecodeError:
        return []


def get_full_path(relative_path: str) -> Path:
    """Get full path from relative path"""
    return UPLOAD_DIR.parent / relative_path


def delete_file(relative_path: str) -> bool:
    """Delete file by relative path"""
    try:
        file_path = get_full_path(relative_path)
        if file_path.exists():
            file_path.unlink()
            return True
    except Exception:
        pass
    return False

