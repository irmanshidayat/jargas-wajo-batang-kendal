from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status, Response, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.config.database import get_db
from app.core.security import get_current_user
from app.core.project_context import get_current_project
from app.models.user.user import User, UserRole
from app.services.inventory import (
    InventoryService,
    MaterialService,
    MandorService,
    StockService,
    NotificationService,
)
from app.services.inventory.surat_permintaan_service import SuratPermintaanService
from app.services.inventory.surat_jalan_service import SuratJalanService
from app.services.inventory.audit_log_service import AuditLogService, ActionType
from app.utils.excel_importer import parse_excel_file, validate_material_row
from app.utils.excel_template import create_material_import_template
from app.schemas.inventory.request import (
    MaterialCreateRequest,
    MaterialUpdateRequest,
    MandorCreateRequest,
    MandorUpdateRequest,
    StockInCreateRequest,
    StockInUpdateRequest,
    StockOutCreateRequest,
    InstalledCreateRequest,
    ReturnCreateRequest,
    ExportExcelRequest,
)
from app.schemas.inventory.surat_permintaan import (
    SuratPermintaanCreateRequest,
    SuratPermintaanUpdateRequest,
    SuratPermintaanResponse,
)
from app.schemas.inventory.surat_jalan_request import (
    SuratJalanCreateRequest,
    SuratJalanUpdateRequest,
    SuratJalanResponse,
)
from app.schemas.inventory.response import (
    MaterialResponse,
    MandorResponse,
    StockInResponse,
    StockOutResponse,
    InstalledResponse,
    ReturnResponse,
    StockBalanceResponse,
    DiscrepancyResponse,
    NotificationResponse,
)
from app.utils.response import success_response, paginated_response, error_response
from app.utils.file_upload import save_uploaded_files, get_evidence_paths_from_db
from app.utils.excel_exporter import create_excel_export
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.helpers import sanitize_dict
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import json
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


def check_role_permission(user: User, allowed_roles: List[UserRole]):
    """Check if user has required role"""
    if user.role not in allowed_roles:
        raise ForbiddenError(f"Hanya {', '.join([r.value for r in allowed_roles])} yang dapat mengakses endpoint ini")


# ========== MATERIAL ROUTES ==========
@router.get(
    "/materials",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all materials",
    tags=["Materials"]
)
async def get_materials(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get all materials"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    skip = (page - 1) * limit
    material_service = MaterialService(db)
    
    if search:
        materials = material_service.search_by_name(search, skip=skip, limit=limit, project_id=project_id)
        total = len(materials)
    else:
        materials, total = material_service.get_all(skip=skip, limit=limit, project_id=project_id)
    
    return paginated_response(
        data=[MaterialResponse.model_validate(m).model_dump(mode="json") for m in materials],
        total=total,
        page=page,
        limit=limit,
        message="Daftar materials berhasil diambil"
    )


@router.get(
    "/materials/{material_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get material by ID",
    tags=["Materials"]
)
async def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get material by ID"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    material_service = MaterialService(db)
    material = material_service.get_by_id(material_id, project_id=project_id)
    
    return success_response(
        data=MaterialResponse.model_validate(material).model_dump(mode="json"),
        message="Data material berhasil diambil"
    )


@router.get(
    "/materials/unique/satuans",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get unique satuan values",
    tags=["Materials"]
)
async def get_unique_satuans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get unique satuan values from all active materials"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    material_service = MaterialService(db)
    satuans = material_service.get_unique_satuans()
    
    return success_response(
        data=satuans,
        message="Daftar satuan berhasil diambil"
    )


@router.get(
    "/materials/unique/kategoris",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get unique kategori values",
    tags=["Materials"]
)
async def get_unique_kategoris(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get unique kategori values from all active materials"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    material_service = MaterialService(db)
    kategoris = material_service.get_unique_kategoris()
    
    return success_response(
        data=kategoris,
        message="Daftar kategori berhasil diambil"
    )


@router.put(
    "/materials/{material_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update material",
    tags=["Materials"]
)
async def update_material(
    material_id: int,
    material_data: MaterialUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Update material"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    material_service = MaterialService(db)
    material = material_service.update(material_id, sanitize_dict(material_data.model_dump(exclude_unset=True)), project_id=project_id)
    
    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.UPDATE,
        table_name="materials",
        record_id=material_id,
        new_values=material_data.model_dump(exclude_unset=True),
        description=f"Update material ID: {material_id}"
    )
    
    return success_response(
        data=MaterialResponse.model_validate(material).model_dump(mode="json"),
        message="Material berhasil diupdate"
    )


@router.delete(
    "/materials/{material_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Delete material",
    tags=["Materials"]
)
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Delete material (hard delete - benar-benar menghapus dari database)"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    material_service = MaterialService(db)
    
    try:
        # Get material before delete for audit log
        material = material_service.get_by_id(material_id, project_id=project_id)
        
        # Delete material (hard delete) - akan validasi terlebih dahulu
        material_service.delete(material_id, project_id=project_id)
        
        # Audit log
        audit_service = AuditLogService(db)
        audit_service.create_log(
            user_id=current_user.id,
            action=ActionType.DELETE,
            table_name="materials",
            record_id=material_id,
            old_values={"kode_barang": material.kode_barang, "nama_barang": material.nama_barang},
            description=f"Delete material ID: {material_id} - {material.nama_barang}"
        )
        
        return success_response(
            data=None,
            message="Material berhasil dihapus"
        )
    except ValidationError as e:
        logger.warning(f"Validation error in delete_material: {str(e)}")
        db.rollback()
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except IntegrityError as e:
        logger.error(f"Integrity error in delete_material: {str(e)}", exc_info=True)
        db.rollback()
        error_msg = str(e)
        if "foreign key constraint" in error_msg.lower():
            return error_response(
                message="Material tidak dapat dihapus karena masih digunakan di data lain (stock in, stock out, installed, return, atau surat permintaan). Hapus data terkait terlebih dahulu.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return error_response(
            message=f"Gagal menghapus material: {error_msg}",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_material: {str(e)}", exc_info=True)
        db.rollback()
        return error_response(
            message="Terjadi kesalahan saat menghapus material",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(
    "/materials",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create material",
    tags=["Materials"]
)
async def create_material(
    material_data: MaterialCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create new material"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    material_service = MaterialService(db)
    material = material_service.create(material_data.model_dump(), project_id=project_id)
    
    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.CREATE,
        table_name="materials",
        record_id=material.id,
        new_values=material_data.model_dump(),
        description=f"Create material: {material_data.kode_barang}"
    )
    
    return success_response(
        data=MaterialResponse.model_validate(material).model_dump(mode="json"),
        message="Material berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/materials/bulk-import",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Bulk import materials from Excel",
    tags=["Materials"]
)
async def bulk_import_materials(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """
    Bulk import materials dari file Excel (.xlsx)
    Format Excel: Header di row 1, data mulai dari row 2
    Kolom: NO, NAMA BARANG, KODE BARANG, SATUAN, KATEGORI, HARGA
    """
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    # Validasi file type
    if not file.filename.endswith('.xlsx'):
        return success_response(
            data=None,
            message="Format file tidak valid. Hanya file .xlsx yang diperbolehkan",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Validasi file size (max 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        return success_response(
            data=None,
            message="Ukuran file terlalu besar. Maksimal 10MB",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Expected headers sesuai dengan format Excel
        expected_headers = ["NO", "NAMA BARANG", "KODE BARANG", "SATUAN", "KATEGORI", "HARGA"]
        
        # Parse Excel file
        rows_data, parse_errors = parse_excel_file(
            file_content=file_content,
            expected_headers=expected_headers,
            start_row=2,  # Data mulai dari row 2 (row 1 adalah header)
            skip_empty_rows=True
        )
        
        if parse_errors:
            return success_response(
                data={
                    'success_count': 0,
                    'failed_count': len(rows_data),
                    'errors': parse_errors
                },
                message="Gagal membaca file Excel",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not rows_data:
            return success_response(
                data={
                    'success_count': 0,
                    'failed_count': 0,
                    'errors': []
                },
                message="File Excel tidak memiliki data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validasi setiap row
        material_service = MaterialService(db)
        valid_kategoris = material_service.get_valid_kategoris()
        
        validated_rows = []
        validation_errors = []
        
        for row in rows_data:
            is_valid, error_msg = validate_material_row(row, valid_kategoris)
            if is_valid:
                validated_rows.append(row)
            else:
                validation_errors.append(error_msg)
        
        # Jika semua row tidak valid
        if not validated_rows:
            return success_response(
                data={
                    'success_count': 0,
                    'validation_failed_count': len(rows_data),
                    'processing_failed_count': 0,
                    'validation_errors': validation_errors,
                    'processing_errors': [],
                    'errors': validation_errors  # Backward compatibility
                },
                message="Tidak ada data yang valid",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Bulk create materials
        logger.info(f"Bulk import: {len(validated_rows)} rows validated, {len(validation_errors)} validation errors")
        result = material_service.bulk_create(validated_rows, project_id=project_id)
        logger.info(f"Bulk import result: {result['success_count']} sukses, {result['failed_count']} gagal, {len(result['errors'])} errors")
        
        # Pisahkan validation errors dan processing errors
        validation_failed_count = len(validation_errors)
        processing_failed_count = result.get('failed_count', 0)
        processing_errors = result.get('errors', [])
        
        # Gabungkan semua errors untuk backward compatibility
        all_errors = validation_errors + processing_errors
        
        # Log semua errors untuk debugging
        if all_errors:
            logger.warning(f"Bulk import errors: {all_errors}")
        
        # Audit log
        audit_service = AuditLogService(db)
        total_failed = validation_failed_count + processing_failed_count
        audit_service.create_log(
            user_id=current_user.id,
            action=ActionType.CREATE,
            table_name="materials",
            record_id=0,  # Bulk operation, tidak punya single record_id
            new_values={"bulk_import": True, "file_name": file.filename},
            description=f"Bulk import materials: {result['success_count']} sukses, {total_failed} gagal (validasi: {validation_failed_count}, proses: {processing_failed_count})"
        )
        
        # Prepare response dengan struktur baru
        response_data = {
            'success_count': result['success_count'],
            'validation_failed_count': validation_failed_count,
            'processing_failed_count': processing_failed_count,
            'validation_errors': validation_errors,
            'processing_errors': processing_errors,
            'errors': all_errors  # Backward compatibility
        }
        
        # Prepare response message - fokus pada data yang berhasil masuk
        if result['success_count'] > 0:
            if validation_failed_count > 0 or processing_failed_count > 0:
                message = f"Berhasil mengimpor {result['success_count']} material"
                if validation_failed_count > 0:
                    message += f", {validation_failed_count} data tidak valid (tidak masuk database)"
                if processing_failed_count > 0:
                    message += f", {processing_failed_count} data gagal saat insert"
            else:
                message = f"Berhasil mengimpor {result['success_count']} material"
        else:
            # Tidak ada yang berhasil
            if validation_failed_count > 0:
                message = f"Gagal mengimpor: {validation_failed_count} data tidak valid"
            elif processing_failed_count > 0:
                message = f"Gagal mengimpor: {processing_failed_count} data gagal saat insert"
            else:
                message = "Gagal mengimpor material"
        
        return success_response(
            data=response_data,
            message=message,
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"Bulk import exception: {error_msg}", exc_info=True)
        return success_response(
            data={
                'success_count': 0,
                'validation_failed_count': 0,
                'processing_failed_count': 0,
                'validation_errors': [],
                'processing_errors': [],
                'errors': [error_msg]  # Backward compatibility
            },
            message="Terjadi kesalahan saat memproses file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/materials-template",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Download Excel template for bulk import",
    tags=["Materials"]
)
async def download_material_import_template(
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """
    Download template Excel untuk bulk import materials
    Template berisi header dan contoh data
    """
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    template_file = create_material_import_template()
    
    from datetime import datetime
    filename = f"template_import_material_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return Response(
        content=template_file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# ========== MANDOR ROUTES ==========
@router.get(
    "/mandors",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all mandors",
    tags=["Mandors"]
)
async def get_mandors(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get all mandors"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    skip = (page - 1) * limit
    mandor_service = MandorService(db)
    
    if search:
        mandors = mandor_service.search_by_name(search, skip=skip, limit=limit, project_id=project_id)
        total = len(mandors)
    else:
        mandors, total = mandor_service.get_all(skip=skip, limit=limit, project_id=project_id)
    
    return paginated_response(
        data=[MandorResponse.model_validate(m).model_dump(mode="json") for m in mandors],
        total=total,
        page=page,
        limit=limit,
        message="Daftar mandors berhasil diambil"
    )


@router.post(
    "/mandors",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create mandor",
    tags=["Mandors"]
)
async def create_mandor(
    mandor_data: MandorCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create new mandor"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    mandor_service = MandorService(db)
    mandor = mandor_service.create(mandor_data.model_dump(), project_id=project_id)
    
    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.CREATE,
        table_name="mandors",
        record_id=mandor.id,
        new_values=mandor_data.model_dump(),
        description=f"Create mandor: {mandor_data.nama}"
    )
    
    return success_response(
        data=MandorResponse.model_validate(mandor).model_dump(mode="json"),
        message="Mandor berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )


# ========== STOCK IN ROUTES ==========
@router.get(
    "/stock-in",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get list stock in",
    tags=["Stock In"]
)
async def get_stock_in_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Ambil daftar barang masuk dengan pagination"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    try:
        skip = (page - 1) * limit
        from sqlalchemy.orm import joinedload, load_only
        from sqlalchemy import or_, and_, func
        from app.models.inventory.stock_in import StockIn
        from app.models.inventory.material import Material

        # Base query dengan eager loading, hindari select kolom yang tidak ada di DB (project_id)
        query = db.query(StockIn).options(
            load_only(
                StockIn.id,
                StockIn.nomor_invoice,
                StockIn.material_id,
                StockIn.quantity,
                StockIn.tanggal_masuk,
                StockIn.evidence_paths,
                StockIn.surat_jalan_paths,
                StockIn.material_datang_paths,
                StockIn.created_at,
                StockIn.updated_at,
            ),
            joinedload(StockIn.material).load_only(
                Material.id,
                Material.kode_barang,
                Material.nama_barang,
                Material.satuan,
            ),
        ).filter(StockIn.is_deleted == 0)
        
        # Filter by project_id if provided
        # Filter melalui material karena stock_ins.project_id mungkin belum ada di database
        if project_id is not None:
            # Join dengan Material dan filter berdasarkan material.project_id
            query = query.join(Material).filter(Material.project_id == project_id)

        # Apply date filters
        if start_date:
            query = query.filter(StockIn.tanggal_masuk >= start_date)
        if end_date:
            query = query.filter(StockIn.tanggal_masuk <= end_date)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Pastikan Material sudah di-join sebelumnya jika sudah ada project_id filter
            if project_id is None:
                query = query.join(Material)
            query = query.filter(
                or_(
                    StockIn.nomor_invoice.ilike(search_term),
                    Material.nama_barang.ilike(search_term),
                    Material.kode_barang.ilike(search_term)
                )
            )

        # Get total count menggunakan func.count untuk menghindari select kolom project_id
        total = query.with_entities(func.count(StockIn.id)).scalar() or 0

        # Apply pagination and ordering
        items = query.order_by(StockIn.id.desc()).offset(skip).limit(limit).all()

        # Ensure relationships are loaded
        for item in items:
            if item.material_id:
                _ = item.material

        return paginated_response(
            data=[StockInResponse.model_validate(it).model_dump(mode="json") for it in items],
            total=total,
            page=page,
            limit=limit,
            message="Daftar barang masuk berhasil diambil"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error getting stock in list: {str(e)}", exc_info=True)
        db.rollback()
        raise ValidationError(f"Gagal mengambil daftar barang masuk: Kesalahan database")
    except Exception as e:
        logger.error(f"Error getting stock in list: {str(e)}", exc_info=True)
        raise ValidationError(f"Gagal mengambil daftar barang masuk: {str(e)}")

@router.post(
    "/stock-in",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create stock in",
    tags=["Stock In"]
)
async def create_stock_in(
    nomor_invoice: str = Form(...),
    material_id: int = Form(...),
    quantity: float = Form(..., gt=0),
    tanggal_masuk: date = Form(...),
    evidence: List[UploadFile] = File(default=[]),
    surat_jalan: List[UploadFile] = File(default=[]),
    material_datang: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create stock in dengan multiple file upload"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    stock_service = StockService(db)
    
    # Save evidence files
    evidence_paths = []
    if evidence:
        evidence_paths = await save_uploaded_files(evidence, "stock_in", 0)
    
    # Save surat jalan files
    surat_jalan_paths = []
    if surat_jalan:
        surat_jalan_paths = await save_uploaded_files(surat_jalan, "stock_in", 0)
    
    # Save material datang files
    material_datang_paths = []
    if material_datang:
        material_datang_paths = await save_uploaded_files(material_datang, "stock_in", 0)
    
    # Create stock in (get ID from created record)
    stock_in = stock_service.create_stock_in(
        nomor_invoice=nomor_invoice,
        material_id=material_id,
        quantity=quantity,
        tanggal_masuk=tanggal_masuk,
        evidence_paths=evidence_paths,
        created_by=current_user.id,
        surat_jalan_paths=surat_jalan_paths,
        material_datang_paths=material_datang_paths,
        project_id=project_id
    )
    
    # Update file paths with actual ID
    if evidence_paths or surat_jalan_paths or material_datang_paths:
        from app.utils.file_upload import save_evidence_paths_to_db
        stock_in_repo = stock_service.stock_in_repo
        update_data = {}
        if evidence_paths:
            update_data["evidence_paths"] = save_evidence_paths_to_db(evidence_paths)
        if surat_jalan_paths:
            update_data["surat_jalan_paths"] = save_evidence_paths_to_db(surat_jalan_paths)
        if material_datang_paths:
            update_data["material_datang_paths"] = save_evidence_paths_to_db(material_datang_paths)
        if update_data:
            stock_in_repo.update(stock_in.id, update_data)
    
    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.CREATE,
        table_name="stock_ins",
        record_id=stock_in.id,
        new_values={
            "nomor_invoice": nomor_invoice,
            "material_id": material_id,
            "quantity": quantity,
            "tanggal_masuk": str(tanggal_masuk)
        },
        description=f"Create stock in: {nomor_invoice}"
    )
    
    return success_response(
        data=StockInResponse.model_validate(stock_in).model_dump(mode="json"),
        message="Barang masuk berhasil dicatat",
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/stock-in/bulk",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple stock in in one invoice",
    tags=["Stock In"]
)
async def create_stock_in_bulk(
    nomor_invoice: str = Form(...),
    tanggal_masuk: date = Form(...),
    items: str = Form(...),  # JSON string array of { material_id, quantity }
    evidence: List[UploadFile] = File(default=[]),
    surat_jalan: List[UploadFile] = File(default=[]),
    material_datang: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create many stock in items under a single invoice. Evidence, surat jalan, dan material datang applies to all items."""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    try:
        logger.info(f"Starting bulk stock-in creation. Invoice: {nomor_invoice}, User: {current_user.id}, Items count: {len(items) if items else 0}")
        
        stock_service = StockService(db)

        # Save evidence files once for the invoice
        evidence_paths = []
        if evidence:
            try:
                logger.info(f"Saving {len(evidence)} evidence files")
                evidence_paths = await save_uploaded_files(evidence, "stock_in", 0)
                logger.info(f"Successfully saved {len(evidence_paths)} evidence files")
            except Exception as e:
                logger.error(f"Error saving evidence files: {str(e)}", exc_info=True)
                return error_response(
                    message=f"Gagal menyimpan file evidence: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Save surat jalan files once for the invoice
        surat_jalan_paths = []
        if surat_jalan:
            try:
                logger.info(f"Saving {len(surat_jalan)} surat jalan files")
                surat_jalan_paths = await save_uploaded_files(surat_jalan, "stock_in", 0)
                logger.info(f"Successfully saved {len(surat_jalan_paths)} surat jalan files")
            except Exception as e:
                logger.error(f"Error saving surat jalan files: {str(e)}", exc_info=True)
                return error_response(
                    message=f"Gagal menyimpan file surat jalan: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Save material datang files once for the invoice
        material_datang_paths = []
        if material_datang:
            try:
                logger.info(f"Saving {len(material_datang)} material datang files")
                material_datang_paths = await save_uploaded_files(material_datang, "stock_in", 0)
                logger.info(f"Successfully saved {len(material_datang_paths)} material datang files")
            except Exception as e:
                logger.error(f"Error saving material datang files: {str(e)}", exc_info=True)
                return error_response(
                    message=f"Gagal menyimpan file material datang: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Parse and validate items JSON
        try:
            logger.info(f"[DEBUG create_stock_in_bulk] Raw items string received: {items[:500] if items else 'None'}")
            parsed_items = json.loads(items)
            logger.info(f"[DEBUG create_stock_in_bulk] Parsed items (after json.loads): {parsed_items}")
            # Log setiap item untuk tracking quantity
            for idx, item in enumerate(parsed_items):
                logger.info(f"[DEBUG create_stock_in_bulk] Item {idx+1} after parse: material_id={item.get('material_id')}, quantity={item.get('quantity')}, quantity_type={type(item.get('quantity'))}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}, Items string: {items[:200] if items else 'None'}")
            return error_response(
                message="Format items tidak valid. Harus berupa JSON array",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing items: {str(e)}", exc_info=True)
            return error_response(
                message=f"Error parsing items: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(parsed_items, list) or len(parsed_items) == 0:
            logger.warning(f"Empty or invalid items list: {parsed_items}")
            return error_response(
                message="Items wajib diisi minimal 1",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Service will do deeper validation including duplicate and material existence
        try:
            logger.info(f"Calling stock_service.create_stock_in_bulk with {len(parsed_items)} items")
            created_items = stock_service.create_stock_in_bulk(
                nomor_invoice=nomor_invoice,
                tanggal_masuk=tanggal_masuk,
                items=parsed_items,
                evidence_paths=evidence_paths,
                created_by=current_user.id,
                surat_jalan_paths=surat_jalan_paths,
                material_datang_paths=material_datang_paths,
                project_id=project_id
            )
            logger.info(f"Successfully created {len(created_items)} stock-in records")
        except ValidationError as e:
            logger.warning(f"Validation error in create_stock_in_bulk: {str(e)}")
            return error_response(
                message=str(e.detail) if hasattr(e, 'detail') else str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except NotFoundError as e:
            logger.warning(f"Not found error in create_stock_in_bulk: {str(e)}")
            return error_response(
                message=str(e.detail) if hasattr(e, 'detail') else str(e),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Database error in create_stock_in_bulk: {str(e)}", exc_info=True)
            db.rollback()
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                return error_response(
                    message="Data material atau user tidak valid. Pastikan material_id dan user_id yang digunakan ada di database.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                return error_response(
                    message="Data duplikat terdeteksi. Pastikan nomor invoice atau data lain tidak duplikat.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            return error_response(
                message=f"Terjadi kesalahan pada database: {error_msg}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_stock_in_bulk: {str(e)}", exc_info=True)
            db.rollback()
            return error_response(
                message=f"Terjadi kesalahan saat membuat stock-in: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Audit log per item (jangan hentikan proses jika logging gagal)
        audit_service = AuditLogService(db)
        audit_success_count = 0
        for si in created_items:
            try:
                audit_service.create_log(
                    user_id=current_user.id,
                    action=ActionType.CREATE,
                    table_name="stock_ins",
                    record_id=si.id,
                    new_values={
                        "nomor_invoice": nomor_invoice,
                        "material_id": si.material_id,
                        "quantity": si.quantity,
                        "tanggal_masuk": str(tanggal_masuk)
                    },
                    description=f"Create stock in (bulk): {nomor_invoice}"
                )
                audit_success_count += 1
            except Exception as audit_err:
                logger.warning(f"Failed to create audit log for stock_in {si.id}: {str(audit_err)}")
        
        logger.info(f"Created {len(created_items)} stock-in records, {audit_success_count} audit logs")

        return success_response(
            data=[StockInResponse.model_validate(si).model_dump(mode="json") for si in created_items],
            message="Barang masuk (bulk) berhasil dicatat",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_stock_in_bulk endpoint: {str(e)}", exc_info=True)
        db.rollback()
        return error_response(
            message=f"Terjadi kesalahan pada server: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put(
    "/stock-in/{stock_in_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update stock in",
    tags=["Stock In"]
)
async def update_stock_in(
    stock_in_id: int,
    nomor_invoice: Optional[str] = Form(None),
    material_id: Optional[int] = Form(None),
    quantity: Optional[Decimal] = Form(None),
    tanggal_masuk: Optional[date] = Form(None),
    evidence: List[UploadFile] = File(default=[]),
    surat_jalan: List[UploadFile] = File(default=[]),
    material_datang: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Update stock in record"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    stock_service = StockService(db)
    
    # Get existing stock in to check if it exists
    existing_stock_in = stock_service.stock_in_repo.get(stock_in_id)
    if not existing_stock_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock in dengan ID {stock_in_id} tidak ditemukan"
        )
    
    if existing_stock_in.is_deleted == 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock in dengan ID {stock_in_id} sudah dihapus"
        )
    
    # Prepare update data
    evidence_paths = None
    if evidence:
        evidence_paths = await save_uploaded_files(evidence, "stock_in", stock_in_id)
    
    surat_jalan_paths = None
    if surat_jalan:
        surat_jalan_paths = await save_uploaded_files(surat_jalan, "stock_in", stock_in_id)
    
    material_datang_paths = None
    if material_datang:
        material_datang_paths = await save_uploaded_files(material_datang, "stock_in", stock_in_id)
    
    # Convert quantity to Decimal if provided
    quantity_decimal = None
    if quantity is not None:
        quantity_decimal = Decimal(str(quantity))
    
    try:
        # Update stock in
        updated_stock_in = stock_service.update_stock_in(
            stock_in_id=stock_in_id,
            nomor_invoice=nomor_invoice,
            material_id=material_id,
            quantity=quantity_decimal,
            tanggal_masuk=tanggal_masuk,
            evidence_paths=evidence_paths,
            surat_jalan_paths=surat_jalan_paths,
            material_datang_paths=material_datang_paths,
            updated_by=current_user.id,
            project_id=project_id
        )
        
        # Update file paths with actual ID if files were uploaded
        if evidence_paths or surat_jalan_paths or material_datang_paths:
            from app.utils.file_upload import save_evidence_paths_to_db
            update_data = {}
            if evidence_paths:
                # Merge with existing evidence if any
                existing_evidence = get_evidence_paths_from_db(existing_stock_in.evidence_paths)
                all_evidence = existing_evidence + evidence_paths
                update_data["evidence_paths"] = save_evidence_paths_to_db(all_evidence)
            if surat_jalan_paths:
                existing_surat_jalan = get_evidence_paths_from_db(existing_stock_in.surat_jalan_paths)
                all_surat_jalan = existing_surat_jalan + surat_jalan_paths
                update_data["surat_jalan_paths"] = save_evidence_paths_to_db(all_surat_jalan)
            if material_datang_paths:
                existing_material_datang = get_evidence_paths_from_db(existing_stock_in.material_datang_paths)
                all_material_datang = existing_material_datang + material_datang_paths
                update_data["material_datang_paths"] = save_evidence_paths_to_db(all_material_datang)
            if update_data:
                stock_service.stock_in_repo.update(stock_in_id, update_data)
                # Refresh the object
                updated_stock_in = stock_service.stock_in_repo.get(stock_in_id)
        
        # Audit log
        audit_service = AuditLogService(db)
        update_values = {}
        if nomor_invoice is not None:
            update_values["nomor_invoice"] = nomor_invoice
        if material_id is not None:
            update_values["material_id"] = material_id
        if quantity is not None:
            update_values["quantity"] = str(quantity)
        if tanggal_masuk is not None:
            update_values["tanggal_masuk"] = str(tanggal_masuk)
        
        audit_service.create_log(
            user_id=current_user.id,
            action=ActionType.UPDATE,
            table_name="stock_ins",
            record_id=stock_in_id,
            new_values=update_values,
            description=f"Update stock in ID: {stock_in_id}"
        )
        
        return success_response(
            data=StockInResponse.model_validate(updated_stock_in).model_dump(mode="json"),
            message="Barang masuk berhasil diupdate"
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating stock in: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengupdate barang masuk: {str(e)}"
        )


# ========== STOCK OUT ROUTES ==========
@router.get(
    "/stock-out",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get list stock out",
    tags=["Stock Out"]
)
async def get_stock_out_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Ambil daftar barang keluar dengan pagination"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    try:
        skip = (page - 1) * limit
        from sqlalchemy.orm import joinedload, load_only
        from sqlalchemy import or_, func, and_
        from app.models.inventory.stock_out import StockOut
        from app.models.inventory.material import Material
        from app.models.inventory.mandor import Mandor
        
        # Base query dengan eager loading, batasi kolom agar tidak menyentuh project_id
        query = db.query(StockOut).options(
            load_only(
                StockOut.id,
                StockOut.nomor_barang_keluar,
                StockOut.mandor_id,
                StockOut.material_id,
                StockOut.quantity,
                StockOut.tanggal_keluar,
                StockOut.evidence_paths,
                StockOut.surat_permohonan_paths,
                StockOut.surat_serah_terima_paths,
                StockOut.created_at,
                StockOut.updated_at,
            ),
            joinedload(StockOut.material).load_only(
                Material.id,
                Material.kode_barang,
                Material.nama_barang,
                Material.satuan,
            ),
            joinedload(StockOut.mandor).load_only(
                Mandor.id,
                Mandor.nama,
            ),
        ).filter(StockOut.is_deleted == 0)
        
        # Exclude stock out yang dibuat dari return (retur keluar)
        # Stock out yang dibuat dari return akan punya Return dengan stock_out_id = stock_out.id dan is_released = 1
        from app.models.inventory.return_model import Return
        from sqlalchemy import not_, exists
        query = query.filter(
            ~exists().where(
                and_(
                    Return.stock_out_id == StockOut.id,
                    Return.is_released == 1,
                    or_(Return.is_deleted == 0, Return.is_deleted.is_(None))
                )
            )
        )
        
        # Filter by project_id jika ada: gunakan Material.project_id (kolom tersedia di DB)
        if project_id is not None:
            query = query.join(Material, StockOut.material_id == Material.id).filter(Material.project_id == project_id)

        # Apply date filters
        if start_date:
            query = query.filter(StockOut.tanggal_keluar >= start_date)
        if end_date:
            query = query.filter(StockOut.tanggal_keluar <= end_date)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Jika belum join Material dari filter project, join sekarang
            if project_id is None:
                query = query.join(Material, StockOut.material_id == Material.id)
            # Pastikan join Mandor untuk pencarian nama mandor
            query = query.join(Mandor, StockOut.mandor_id == Mandor.id).filter(
                or_(
                    StockOut.nomor_barang_keluar.ilike(search_term),
                    Material.nama_barang.ilike(search_term),
                    Material.kode_barang.ilike(search_term),
                    Mandor.nama.ilike(search_term)
                )
            )
        
        # Get total count aman (hindari select kolom yang tidak ada)
        total = query.with_entities(func.count(StockOut.id)).scalar() or 0
        
        # Apply pagination and ordering
        items = query.order_by(StockOut.id.desc()).offset(skip).limit(limit).all()
        
        # Pastikan semua relationship ter-load sebelum serialize
        for item in items:
            if item.material_id:
                _ = item.material
            if item.mandor_id:
                _ = item.mandor

        return paginated_response(
            data=[StockOutResponse.model_validate(it).model_dump(mode="json") for it in items],
            total=total,
            page=page,
            limit=limit,
            message="Daftar barang keluar berhasil diambil"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error getting stock out list: {str(e)}", exc_info=True)
        db.rollback()
        raise ValidationError(f"Gagal mengambil daftar barang keluar: Kesalahan database")
    except Exception as e:
        logger.error(f"Error getting stock out list: {str(e)}", exc_info=True)
        raise ValidationError(f"Gagal mengambil daftar barang keluar: {str(e)}")

@router.get(
    "/stock-out/by-mandor/{mandor_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get stock outs by mandor ID dengan informasi sisa quantity",
    tags=["Stock Out"]
)
async def get_stock_outs_by_mandor(
    mandor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get stock outs by mandor untuk digunakan di dropdown form installed.
    
    Menambahkan informasi:
    - quantity_terpasang: total quantity yang sudah terpasang
    - quantity_sisa_kembali: sisa barang kembali (Barang Keluar - Barang Terpasang)
    - quantity_sudah_kembali: total quantity yang sudah dikembalikan (untuk informasi)
    - quantity_sisa: sisa quantity yang bisa dikembalikan (untuk backward compatibility)
    """
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        stock_service = StockService(db)

        # Build query seperti list stock-out, namun difokuskan pada mandor yang diminta
        from sqlalchemy.orm import joinedload, load_only
        from sqlalchemy import and_, or_, exists
        from app.models.inventory.stock_out import StockOut
        from app.models.inventory.material import Material
        from app.models.inventory.mandor import Mandor
        from app.models.inventory.return_model import Return

        query = db.query(StockOut).options(
            load_only(
                StockOut.id,
                StockOut.nomor_barang_keluar,
                StockOut.mandor_id,
                StockOut.material_id,
                StockOut.quantity,
                StockOut.tanggal_keluar,
                StockOut.evidence_paths,
                StockOut.surat_permohonan_paths,
                StockOut.surat_serah_terima_paths,
                StockOut.created_at,
                StockOut.updated_at,
            ),
            joinedload(StockOut.material).load_only(
                Material.id,
                Material.kode_barang,
                Material.nama_barang,
                Material.satuan,
            ),
            joinedload(StockOut.mandor).load_only(
                Mandor.id,
                Mandor.nama,
            ),
        ).filter(
            StockOut.is_deleted == 0,
            StockOut.mandor_id == mandor_id,
        )

        # Exclude stock out yang dibuat dari return (retur keluar)
        query = query.filter(
            ~exists().where(
                and_(
                    Return.stock_out_id == StockOut.id,
                    Return.is_released == 1,
                    or_(Return.is_deleted == 0, Return.is_deleted.is_(None))
                )
            )
        )

        # Filter by project_id jika ada: gunakan Material.project_id
        if project_id is not None:
            query = query.join(Material, StockOut.material_id == Material.id).filter(Material.project_id == project_id)

        stock_outs = query.order_by(StockOut.id.desc()).limit(1000).all()
        
        # Hitung quantity_terpasang per SO hanya dari pemasangan yang tertaut langsung (strict by stock_out_id)
        result_data = []
        from sqlalchemy import func
        from app.models.inventory.installed import Installed

        so_ids = [so.id for so in stock_outs]
        linked_installed_sum_by_so: dict[int, int] = {}
        if so_ids:
            rows = (
                db.query(Installed.stock_out_id, func.coalesce(func.sum(Installed.quantity), 0))
                .filter(Installed.is_deleted == 0)
                .filter(Installed.stock_out_id.in_(so_ids))
                .group_by(Installed.stock_out_id)
                .all()
            )
            linked_installed_sum_by_so = {row[0]: int(row[1] or 0) for row in rows}

        for so in stock_outs:
            stock_out_dict = StockOutResponse.model_validate(so).model_dump(mode="json")
            terpasang = max(0, int(linked_installed_sum_by_so.get(so.id, 0)))
            # Get total kondisi reject untuk stock_out_id ini
            total_reject = stock_service.return_repo.get_total_reject_by_stock_out(so.id)
            # Rumus Sisa Bisa Dipasang: Quantity Keluar - Terpasang - Reject (barang reject tidak bisa dipasang)
            sisa = max(0, (so.quantity or 0) - terpasang - total_reject)
            total_quantity_kembali = stock_service.return_repo.get_total_quantity_by_stock_out(so.id)

            stock_out_dict["quantity_terpasang"] = terpasang
            stock_out_dict["quantity_sisa_kembali"] = sisa
            stock_out_dict["quantity_sudah_kembali"] = max(0, total_quantity_kembali)
            stock_out_dict["quantity_sisa"] = sisa

            result_data.append(stock_out_dict)
        
        return success_response(
            data=result_data,
            message="Daftar barang keluar berhasil diambil"
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting stock outs by mandor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil daftar barang keluar: {str(e)}"
        )

@router.get(
    "/stock-out/by-nomor/{nomor_barang_keluar}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get stock outs by nomor barang keluar",
    tags=["Stock Out"]
)
async def get_stock_outs_by_nomor(
    nomor_barang_keluar: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get semua stock out berdasarkan nomor barang keluar untuk digunakan di form surat jalan"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        from sqlalchemy.orm import joinedload, load_only
        from sqlalchemy import and_, or_, exists
        from app.models.inventory.stock_out import StockOut
        from app.models.inventory.material import Material
        from app.models.inventory.mandor import Mandor
        from app.models.inventory.return_model import Return
        
        query = db.query(StockOut).options(
            load_only(
                StockOut.id,
                StockOut.nomor_barang_keluar,
                StockOut.mandor_id,
                StockOut.material_id,
                StockOut.quantity,
                StockOut.tanggal_keluar,
                StockOut.evidence_paths,
                StockOut.surat_permohonan_paths,
                StockOut.surat_serah_terima_paths,
                StockOut.created_at,
                StockOut.updated_at,
            ),
            joinedload(StockOut.material).load_only(
                Material.id,
                Material.kode_barang,
                Material.nama_barang,
                Material.satuan,
            ),
            joinedload(StockOut.mandor).load_only(
                Mandor.id,
                Mandor.nama,
            ),
        ).filter(
            StockOut.is_deleted == 0,
            StockOut.nomor_barang_keluar == nomor_barang_keluar,
        )
        
        # Exclude stock out yang dibuat dari return (retur keluar)
        query = query.filter(
            ~exists().where(
                and_(
                    Return.stock_out_id == StockOut.id,
                    Return.is_released == 1,
                    or_(Return.is_deleted == 0, Return.is_deleted.is_(None))
                )
            )
        )
        
        # Filter by project_id jika ada: gunakan Material.project_id
        if project_id is not None:
            query = query.join(Material, StockOut.material_id == Material.id).filter(Material.project_id == project_id)
        
        stock_outs = query.order_by(StockOut.id.asc()).all()
        
        # Pastikan semua relationship ter-load sebelum serialize
        for item in stock_outs:
            if item.material_id:
                _ = item.material
            if item.mandor_id:
                _ = item.mandor
        
        result_data = [StockOutResponse.model_validate(so).model_dump(mode="json") for so in stock_outs]
        
        return success_response(
            data=result_data,
            message="Daftar barang keluar berhasil diambil"
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting stock outs by nomor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil daftar barang keluar: {str(e)}"
        )

@router.post(
    "/stock-out",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create stock out",
    tags=["Stock Out"]
)
async def create_stock_out(
    mandor_id: int = Form(...),
    material_id: int = Form(...),
    quantity: float = Form(..., gt=0),
    tanggal_keluar: date = Form(...),
    evidence: List[UploadFile] = File(default=[]),
    surat_permohonan: List[UploadFile] = File(default=[]),
    surat_serah_terima: List[UploadFile] = File(default=[]),
    nomor_surat_permintaan: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create stock out dengan auto-numbering atau menggunakan nomor surat permintaan"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    stock_service = StockService(db)
    
    # Save evidence files
    evidence_paths = []
    if evidence:
        evidence_paths = await save_uploaded_files(evidence, "stock_out", 0)
    
    # Save surat permohonan files
    surat_permohonan_paths = []
    if surat_permohonan:
        surat_permohonan_paths = await save_uploaded_files(surat_permohonan, "stock_out", 0)
    
    # Save surat serah terima files
    surat_serah_terima_paths = []
    if surat_serah_terima:
        surat_serah_terima_paths = await save_uploaded_files(surat_serah_terima, "stock_out", 0)
    
    # Create stock out (auto-generate nomor atau gunakan nomor surat permintaan)
    stock_out = stock_service.create_stock_out(
        mandor_id=mandor_id,
        material_id=material_id,
        quantity=quantity,
        tanggal_keluar=tanggal_keluar,
        evidence_paths=evidence_paths,
        created_by=current_user.id,
        surat_permohonan_paths=surat_permohonan_paths,
        surat_serah_terima_paths=surat_serah_terima_paths,
        project_id=project_id,
        nomor_surat_permintaan=nomor_surat_permintaan if nomor_surat_permintaan else None
    )
    
    # Update file paths with actual ID
    if evidence_paths or surat_permohonan_paths or surat_serah_terima_paths:
        from app.utils.file_upload import save_evidence_paths_to_db
        stock_out_repo = stock_service.stock_out_repo
        update_data = {}
        if evidence_paths:
            update_data["evidence_paths"] = save_evidence_paths_to_db(evidence_paths)
        if surat_permohonan_paths:
            update_data["surat_permohonan_paths"] = save_evidence_paths_to_db(surat_permohonan_paths)
        if surat_serah_terima_paths:
            update_data["surat_serah_terima_paths"] = save_evidence_paths_to_db(surat_serah_terima_paths)
        if update_data:
            stock_out_repo.update(stock_out.id, update_data)
    
    # Check discrepancy after create
    notification_service = NotificationService(db)
    notification_service.check_discrepancy()
    
    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.CREATE,
        table_name="stock_outs",
        record_id=stock_out.id,
        new_values={
            "nomor_barang_keluar": stock_out.nomor_barang_keluar,
            "mandor_id": mandor_id,
            "material_id": material_id,
            "quantity": quantity,
            "tanggal_keluar": str(tanggal_keluar)
        },
        description=f"Create stock out: {stock_out.nomor_barang_keluar}"
    )
    
    return success_response(
        data=StockOutResponse.model_validate(stock_out).model_dump(mode="json"),
        message="Barang keluar berhasil dicatat",
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/stock-out/bulk",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple stock out for one mandor",
    tags=["Stock Out"]
)
async def create_stock_out_bulk(
    mandor_id: int = Form(...),
    tanggal_keluar: date = Form(...),
    items: str = Form(...),  # JSON string array of { material_id, quantity }
    evidence: List[UploadFile] = File(default=[]),
    surat_permohonan: List[UploadFile] = File(default=[]),
    surat_serah_terima: List[UploadFile] = File(default=[]),
    nomor_surat_permintaan: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create many stock out items for one mandor on one date. Evidence, surat permohonan, dan surat serah terima applies to all items. 
    Jika nomor_surat_permintaan diisi, semua item akan menggunakan nomor tersebut (dengan suffix jika multiple items).
    Jika tidak, setiap item gets its own auto-generated nomor_barang_keluar."""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    try:
        logger.info(f"Starting bulk stock-out creation. Mandor: {mandor_id}, User: {current_user.id}, Items count: {len(items) if items else 0}")
        
        stock_service = StockService(db)

        # Save evidence files once for the batch
        evidence_paths = []
        if evidence:
            try:
                logger.info(f"Saving {len(evidence)} evidence files")
                evidence_paths = await save_uploaded_files(evidence, "stock_out", 0)
                logger.info(f"Successfully saved {len(evidence_paths)} evidence files")
            except Exception as e:
                logger.error(f"Error saving evidence files: {str(e)}", exc_info=True)
                return error_response(
                    message=f"Gagal menyimpan file evidence: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Save surat permohonan files once for the batch
        surat_permohonan_paths = []
        if surat_permohonan:
            try:
                logger.info(f"Saving {len(surat_permohonan)} surat permohonan files")
                surat_permohonan_paths = await save_uploaded_files(surat_permohonan, "stock_out", 0)
                logger.info(f"Successfully saved {len(surat_permohonan_paths)} surat permohonan files")
            except Exception as e:
                logger.error(f"Error saving surat permohonan files: {str(e)}", exc_info=True)
                return error_response(
                    message=f"Gagal menyimpan file surat permohonan: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Save surat serah terima files once for the batch
        surat_serah_terima_paths = []
        if surat_serah_terima:
            try:
                logger.info(f"Saving {len(surat_serah_terima)} surat serah terima files")
                surat_serah_terima_paths = await save_uploaded_files(surat_serah_terima, "stock_out", 0)
                logger.info(f"Successfully saved {len(surat_serah_terima_paths)} surat serah terima files")
            except Exception as e:
                logger.error(f"Error saving surat serah terima files: {str(e)}", exc_info=True)
                return error_response(
                    message=f"Gagal menyimpan file surat serah terima: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Parse and validate items JSON
        try:
            parsed_items = json.loads(items)
            logger.debug(f"Parsed items: {parsed_items}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}, Items string: {items[:200] if items else 'None'}")
            return error_response(
                message="Format items tidak valid. Harus berupa JSON array",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing items: {str(e)}", exc_info=True)
            return error_response(
                message=f"Error parsing items: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(parsed_items, list) or len(parsed_items) == 0:
            logger.warning(f"Empty or invalid items list: {parsed_items}")
            return error_response(
                message="Items wajib diisi minimal 1",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Service will do deeper validation including duplicate, material existence, and stock availability
        try:
            logger.info(f"Calling stock_service.create_stock_out_bulk with {len(parsed_items)} items, nomor_surat_permintaan={nomor_surat_permintaan}")
            created_items = stock_service.create_stock_out_bulk(
                mandor_id=mandor_id,
                tanggal_keluar=tanggal_keluar,
                items=parsed_items,
                evidence_paths=evidence_paths,
                created_by=current_user.id,
                surat_permohonan_paths=surat_permohonan_paths,
                surat_serah_terima_paths=surat_serah_terima_paths,
                nomor_surat_permintaan=nomor_surat_permintaan if nomor_surat_permintaan else None,
                project_id=project_id
            )
            logger.info(f"Successfully created {len(created_items)} stock-out records")
        except ValidationError as e:
            logger.warning(f"Validation error in create_stock_out_bulk: {str(e)}")
            return error_response(
                message=str(e.detail) if hasattr(e, 'detail') else str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except NotFoundError as e:
            logger.warning(f"Not found error in create_stock_out_bulk: {str(e)}")
            return error_response(
                message=str(e.detail) if hasattr(e, 'detail') else str(e),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Database error in create_stock_out_bulk: {str(e)}", exc_info=True)
            db.rollback()
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                return error_response(
                    message="Data material, mandor, atau user tidak valid. Pastikan material_id, mandor_id, dan user_id yang digunakan ada di database.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                return error_response(
                    message="Data duplikat terdeteksi. Pastikan nomor barang keluar atau data lain tidak duplikat.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            return error_response(
                message=f"Terjadi kesalahan pada database: {error_msg}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_stock_out_bulk: {str(e)}", exc_info=True)
            db.rollback()
            return error_response(
                message=f"Terjadi kesalahan saat membuat stock-out: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Update evidence paths with actual IDs (service already saved, but update if needed)
        if evidence_paths:
            from app.utils.file_upload import save_evidence_paths_to_db
            stock_out_repo = stock_service.stock_out_repo
            for so in created_items:
                stock_out_repo.update(so.id, {
                    "evidence_paths": save_evidence_paths_to_db(evidence_paths)
                })

        # Check discrepancy after create
        notification_service = NotificationService(db)
        notification_service.check_discrepancy()

        # Audit log per item (jangan hentikan proses jika logging gagal)
        audit_service = AuditLogService(db)
        audit_success_count = 0
        for so in created_items:
            try:
                audit_service.create_log(
                    user_id=current_user.id,
                    action=ActionType.CREATE,
                    table_name="stock_outs",
                    record_id=so.id,
                    new_values={
                        "nomor_barang_keluar": so.nomor_barang_keluar,
                        "mandor_id": mandor_id,
                        "material_id": so.material_id,
                        "quantity": so.quantity,
                        "tanggal_keluar": str(tanggal_keluar)
                    },
                    description=f"Create stock out (bulk): {so.nomor_barang_keluar}"
                )
                audit_success_count += 1
            except Exception as audit_err:
                logger.warning(f"Failed to create audit log for stock_out {so.id}: {str(audit_err)}")
        
        logger.info(f"Created {len(created_items)} stock-out records, {audit_success_count} audit logs")

        return success_response(
            data=[StockOutResponse.model_validate(so).model_dump(mode="json") for so in created_items],
            message="Barang keluar (bulk) berhasil dicatat",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_stock_out_bulk endpoint: {str(e)}", exc_info=True)
        db.rollback()
        return error_response(
            message=f"Terjadi kesalahan pada server: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== INSTALLED ROUTES ==========
@router.get(
    "/installed",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get list installed",
    tags=["Installed"]
)
async def get_installed_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Ambil daftar barang terpasang dengan pagination"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    try:
        skip = (page - 1) * limit
        from sqlalchemy.orm import joinedload, load_only
        from sqlalchemy import or_, func
        from app.models.inventory.installed import Installed
        from app.models.inventory.material import Material
        from app.models.inventory.mandor import Mandor
        from app.models.inventory.stock_out import StockOut
        
        # Base query dengan eager loading, batasi kolom agar tidak menyentuh installed.project_id
        query = db.query(Installed).options(
            load_only(
                Installed.id,
                Installed.material_id,
                Installed.quantity,
                Installed.tanggal_pasang,
                Installed.mandor_id,
                Installed.stock_out_id,
                Installed.evidence_paths,
                Installed.no_register,
                Installed.created_at,
                Installed.updated_at,
            ),
            joinedload(Installed.material).load_only(
                Material.id,
                Material.kode_barang,
                Material.nama_barang,
                Material.satuan,
            ),
            joinedload(Installed.mandor).load_only(
                Mandor.id,
                Mandor.nama,
            ),
            joinedload(Installed.stock_out).load_only(
                StockOut.id,
                StockOut.nomor_barang_keluar,
            ),
        ).filter(Installed.is_deleted == 0)
        
        # Filter by project_id jika ada: gunakan Material.project_id (tersedia di DB)
        if project_id is not None:
            query = query.join(Material, Installed.material_id == Material.id).filter(Material.project_id == project_id)

        # Apply date filters
        if start_date:
            query = query.filter(Installed.tanggal_pasang >= start_date)
        if end_date:
            query = query.filter(Installed.tanggal_pasang <= end_date)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Jika belum di-join Material dari filter project, join sekarang
            if project_id is None:
                query = query.join(Material, Installed.material_id == Material.id)
            query = query.join(Mandor, Installed.mandor_id == Mandor.id).filter(
                or_(
                    Installed.no_register.ilike(search_term),
                    Material.nama_barang.ilike(search_term),
                    Material.kode_barang.ilike(search_term),
                    Mandor.nama.ilike(search_term)
                )
            )
        
        # Get total count aman
        total = query.with_entities(func.count(Installed.id)).scalar() or 0
        
        # Apply pagination and ordering
        items = query.order_by(Installed.id.desc()).offset(skip).limit(limit).all()
        
        # Pastikan semua relationship ter-load sebelum serialize
        for item in items:
            if item.material_id:
                _ = item.material
            if item.mandor_id:
                _ = item.mandor

        return paginated_response(
            data=[InstalledResponse.model_validate(it).model_dump(mode="json") for it in items],
            total=total,
            page=page,
            limit=limit,
            message="Daftar barang terpasang berhasil diambil"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error getting installed list: {str(e)}", exc_info=True)
        db.rollback()
        raise ValidationError(f"Gagal mengambil daftar barang terpasang: Kesalahan database")
    except Exception as e:
        logger.error(f"Error getting installed list: {str(e)}", exc_info=True)
        raise ValidationError(f"Gagal mengambil daftar barang terpasang: {str(e)}")

@router.post(
    "/installed",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create installed",
    tags=["Installed"]
)
async def create_installed(
    material_id: int = Form(...),
    quantity: float = Form(..., gt=0),
    tanggal_pasang: date = Form(...),
    mandor_id: int = Form(...),
    stock_out_id: Optional[int] = Form(None),
    no_register: Optional[str] = Form(None),
    evidence: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create installed dengan multiple file upload"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    stock_service = StockService(db)
    
    # Save evidence files
    evidence_paths = []
    if evidence:
        evidence_paths = await save_uploaded_files(evidence, "installed", 0)
    
    # Create installed
    installed = stock_service.create_installed(
        material_id=material_id,
        quantity=quantity,
        tanggal_pasang=tanggal_pasang,
        mandor_id=mandor_id,
        stock_out_id=stock_out_id,
        no_register=no_register,
        evidence_paths=evidence_paths,
        created_by=current_user.id,
        project_id=project_id
    )
    
    # Update evidence paths with actual ID
    if evidence_paths:
        from app.utils.file_upload import save_evidence_paths_to_db
        installed_repo = stock_service.installed_repo
        installed_repo.update(installed.id, {
            "evidence_paths": save_evidence_paths_to_db(evidence_paths)
        })
    
    # Check discrepancy after create
    notification_service = NotificationService(db)
    notification_service.check_discrepancy()
    
    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.CREATE,
        table_name="installed",
        record_id=installed.id,
        new_values={
            "material_id": material_id,
            "quantity": quantity,
            "tanggal_pasang": str(tanggal_pasang),
            "mandor_id": mandor_id,
            "no_register": no_register
        },
        description="Create installed item"
    )
    
    return success_response(
        data=InstalledResponse.model_validate(installed).model_dump(mode="json"),
        message="Barang terpasang berhasil dicatat",
        status_code=status.HTTP_201_CREATED
    )


# ========== RETURN ROUTES ==========
@router.post(
    "/returns",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create return",
    tags=["Returns"]
)
async def create_return(
    mandor_id: int = Form(...),
    material_id: int = Form(...),
    quantity_kembali: float = Form(..., gt=0),
    quantity_kondisi_baik: Optional[float] = Form(None),
    quantity_kondisi_reject: Optional[float] = Form(None),
    nomor_barang_keluar: Optional[str] = Form(None),  # Nomor barang keluar (string)
    stock_out_id: Optional[int] = Form(None),  # Atau bisa pakai stock_out_id langsung
    tanggal_kembali: date = Form(...),
    evidence: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create return dengan multiple file upload
    
    Bisa menggunakan nomor_barang_keluar (string) atau stock_out_id (int).
    Jika nomor_barang_keluar diisi, akan dicari stock_out_id-nya.
    """
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    stock_service = StockService(db)
    try:
        # Resolve stock_out_id dari nomor_barang_keluar jika diisi
        resolved_stock_out_id = stock_out_id
        if nomor_barang_keluar and not stock_out_id:
            stock_out = stock_service.stock_out_repo.get_by_nomor(nomor_barang_keluar)
            if not stock_out:
                raise NotFoundError(f"Stock out dengan nomor {nomor_barang_keluar} tidak ditemukan")
            if stock_out.is_deleted == 1:
                raise ValidationError(f"Stock out dengan nomor {nomor_barang_keluar} sudah dihapus")
            # Wajib memiliki project_id dan harus sesuai dengan project aktif.
            # Jika belum ada project_id, coba set otomatis dari project aktif (dengan validasi material jika tersedia)
            if getattr(stock_out, "project_id", None) is None:
                try:
                    material = stock_service.material_repo.get(stock_out.material_id)
                    if material and getattr(material, "project_id", None) is not None and material.project_id != project_id:
                        raise ValidationError(
                            f"Stock out dengan nomor {nomor_barang_keluar} material-nya bukan milik project ini"
                        )
                    # Set project_id ke project aktif
                    stock_service.stock_out_repo.update(stock_out.id, {"project_id": project_id})
                    stock_out.project_id = project_id
                except Exception:
                    # Jika gagal update karena alasan apa pun, tetap error seperti sebelumnya
                    raise ValidationError(f"Stock out dengan nomor {nomor_barang_keluar} tidak memiliki project_id")
            if stock_out.project_id != project_id:
                raise ValidationError(f"Stock out dengan nomor {nomor_barang_keluar} bukan milik project ini")
            resolved_stock_out_id = stock_out.id
        
        if not resolved_stock_out_id:
            raise ValidationError("Nomor Barang Keluar atau Stock Out ID wajib diisi")

        # Validasi quantity kondisi baik dan reject
        quantity_baik = quantity_kondisi_baik or 0
        quantity_reject = quantity_kondisi_reject or 0
        
        logger.info(f"[DEBUG] Return validation - quantity_kondisi_baik: {quantity_kondisi_baik} -> {quantity_baik}, "
                   f"quantity_kondisi_reject: {quantity_kondisi_reject} -> {quantity_reject}, "
                   f"quantity_kembali: {quantity_kembali}")
        
        # Validasi: quantity kondisi baik dan reject harus >= 0
        if quantity_baik < 0 or quantity_reject < 0:
            raise ValidationError("Quantity kondisi baik dan reject tidak boleh negatif")
        
        # Validasi: total quantity kondisi baik + reject harus > 0
        total_kondisi = quantity_baik + quantity_reject
        logger.info(f"[DEBUG] Return validation - total_kondisi: {total_kondisi}, quantity_kembali: {quantity_kembali}")
        
        if total_kondisi <= 0:
            raise ValidationError(
                f"Total quantity kondisi baik dan reject harus lebih dari 0. Saat ini total: {total_kondisi}. "
                f"Silakan isi salah satu atau kedua field dengan nilai yang sesuai (total tidak boleh 0)."
            )
        
        # Validasi: jumlah quantity kondisi baik + reject tidak boleh lebih dari quantity_kembali
        if total_kondisi > quantity_kembali:
            raise ValidationError(
                f"Jumlah quantity kondisi baik ({quantity_baik}) + kondisi reject ({quantity_reject}) = {total_kondisi} "
                f"tidak boleh lebih dari quantity kembali ({quantity_kembali})"
            )

        # Save evidence files
        evidence_paths = []
        if evidence:
            evidence_paths = await save_uploaded_files(evidence, "return", 0)

        # Create return dengan stock_out_id yang sudah di-resolve
        return_item = stock_service.create_return(
            mandor_id=mandor_id,
            material_id=material_id,
            quantity_kembali=quantity_kembali,
            quantity_kondisi_baik=quantity_kondisi_baik,
            quantity_kondisi_reject=quantity_kondisi_reject,
            stock_out_id=resolved_stock_out_id,
            tanggal_kembali=tanggal_kembali,
            evidence_paths=evidence_paths,
            created_by=current_user.id,
            project_id=project_id
        )

        # Update evidence paths with actual ID
        if evidence_paths:
            from app.utils.file_upload import save_evidence_paths_to_db
            return_repo = stock_service.return_repo
            return_repo.update(return_item.id, {
                "evidence_paths": save_evidence_paths_to_db(evidence_paths)
            })

        # Check discrepancy after create
        notification_service = NotificationService(db)
        notification_service.check_discrepancy()

        # Audit log
        audit_service = AuditLogService(db)
        audit_service.create_log(
            user_id=current_user.id,
            action=ActionType.CREATE,
            table_name="returns",
            record_id=return_item.id,
            new_values={
                "mandor_id": mandor_id,
                "material_id": material_id,
                "quantity_kembali": quantity_kembali,
                "quantity_kondisi_baik": quantity_kondisi_baik,
                "quantity_kondisi_reject": quantity_kondisi_reject,
                "tanggal_kembali": str(tanggal_kembali)
            },
            description="Create return item"
        )

        return success_response(
            data=ReturnResponse.model_validate(return_item).model_dump(mode="json"),
            message="Barang pengembalian berhasil dicatat",
            status_code=status.HTTP_201_CREATED
        )
    except (ValidationError, NotFoundError) as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal mencatat retur barang")


@router.get(
    "/returns",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get returns",
    tags=["Returns"]
)
async def get_returns(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    is_released: Optional[bool] = Query(None),
    mandor_id: Optional[int] = Query(None),
    material_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get list of returns with optional filters"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    try:
        skip = (page - 1) * limit
        from sqlalchemy.orm import joinedload, load_only
        from sqlalchemy import or_, func
        from app.models.inventory.return_model import Return
        from app.models.inventory.material import Material
        from app.models.inventory.mandor import Mandor
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Base query
        query = db.query(Return).filter(Return.is_deleted == 0)
        
        # Filter by project_id langsung di returns.project_id
        if project_id is not None:
            query = query.filter(Return.project_id == project_id)
        
        # Apply existing filters
        if is_released is not None:
            filter_value = 1 if is_released else 0
            query = query.filter(Return.is_released == filter_value)
        if mandor_id is not None:
            query = query.filter(Return.mandor_id == mandor_id)
        if material_id is not None:
            query = query.filter(Return.material_id == material_id)

        # Apply date filters
        if start_date:
            query = query.filter(Return.tanggal_kembali >= start_date)
        if end_date:
            query = query.filter(Return.tanggal_kembali <= end_date)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            # Join Material & Mandor untuk search
            query = query.join(Material, Return.material_id == Material.id)
            query = query.join(Mandor, Return.mandor_id == Mandor.id).filter(
                or_(
                    Material.nama_barang.ilike(search_term),
                    Material.kode_barang.ilike(search_term),
                    Mandor.nama.ilike(search_term)
                )
            )
        
        # Get total count
        if search:
            total = query.with_entities(func.count(func.distinct(Return.id))).scalar() or 0
        else:
            total = query.with_entities(func.count(Return.id)).scalar() or 0
        
        logger.info(f"Query returns: total={total}, project_id={project_id}, page={page}, limit={limit}, search={'Y' if search else 'N'}")
        
        # Apply eager loading dan pagination
        from app.models.inventory.stock_out import StockOut
        query = query.options(
            joinedload(Return.material).load_only(
                Material.id,
                Material.kode_barang,
                Material.nama_barang,
                Material.satuan,
            ),
            joinedload(Return.mandor).load_only(
                Mandor.id,
                Mandor.nama,
            ),
            joinedload(Return.stock_out).load_only(
                StockOut.id,
                StockOut.nomor_barang_keluar,
            ),
        )
        
        items = query.order_by(Return.id.desc()).offset(skip).limit(limit).all()
        
        logger.info(f"Found {len(items)} returns in database")
        
        # Convert to response format
        result_data = []
        for r in items:
            try:
                result_data.append(ReturnResponse.model_validate(r).model_dump(mode="json"))
            except Exception as e:
                logger.error(f"Error validating return {r.id}: {str(e)}", exc_info=True)
                logger.error(f"Return data: id={r.id}, material_id={r.material_id}, mandor_id={r.mandor_id}")
                # Skip this item if validation fails
                continue
        
        logger.info(f"Successfully validated {len(result_data)} returns")

        return paginated_response(
            data=result_data,
            total=total,
            page=page,
            limit=limit,
            message="Daftar returns berhasil diambil"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_returns: {str(e)}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil daftar returns: {str(e)}"
        )


@router.get(
    "/returns/{return_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get return by ID",
    tags=["Returns"]
)
async def get_return_detail(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get single return"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    stock_service = StockService(db)
    ret = stock_service.return_repo.get(return_id)
    if not ret or ret.is_deleted == 1:
        raise NotFoundError(f"Return dengan ID {return_id} tidak ditemukan")

    return success_response(
        data=ReturnResponse.model_validate(ret).model_dump(mode="json"),
        message="Data return berhasil diambil"
    )


@router.post(
    "/returns/{return_id}/stock-out",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Release return to stock out",
    tags=["Returns"]
)
async def release_return_to_stock_out(
    return_id: int,
    tanggal_keluar: date = Form(...),
    evidence: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create stock out record from an existing return and mark it released"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])

    stock_service = StockService(db)

    # Save evidence files
    evidence_paths = []
    if evidence:
        evidence_paths = await save_uploaded_files(evidence, "stock_out", 0)

    stock_out = stock_service.release_return_to_stock_out(
        return_id=return_id,
        tanggal_keluar=tanggal_keluar,
        evidence_paths=evidence_paths,
        created_by=current_user.id,
        project_id=project_id
    )

    # Update evidence paths with actual ID
    if evidence_paths:
        from app.utils.file_upload import save_evidence_paths_to_db
        stock_out_repo = stock_service.stock_out_repo
        stock_out_repo.update(stock_out.id, {
            "evidence_paths": save_evidence_paths_to_db(evidence_paths)
        })

    # Audit log
    audit_service = AuditLogService(db)
    audit_service.create_log(
        user_id=current_user.id,
        action=ActionType.CREATE,
        table_name="stock_outs",
        record_id=stock_out.id,
        new_values={
            "nomor_barang_keluar": stock_out.nomor_barang_keluar,
            "tanggal_keluar": str(tanggal_keluar),
        },
        description=f"Release return to stock out: return_id={return_id}"
    )

    # Refresh return detail for response if needed
    ret = stock_service.return_repo.get(return_id)

    return success_response(
        data={
            "stock_out": StockOutResponse.model_validate(stock_out).model_dump(mode="json"),
            "return": ReturnResponse.model_validate(ret).model_dump(mode="json"),
        },
        message="Return berhasil dikeluarkan kembali",
        status_code=status.HTTP_201_CREATED
    )


# ========== STOCK BALANCE ROUTES ==========
@router.get(
    "/stock-balance",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get stock balance",
    tags=["Stock"]
)
async def get_stock_balance(
    material_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get current stock balance"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    stock_service = StockService(db)
    balance = stock_service.get_stock_balance(
        material_id=material_id, 
        search=search,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id
    )
    
    return success_response(
        data=balance,
        message="Stock balance berhasil diambil"
    )


# ========== DISCREPANCY ROUTES ==========
@router.get(
    "/discrepancy",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Check discrepancy",
    tags=["Notifications"]
)
async def check_discrepancy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Check discrepancy antara barang keluar dan terpasang"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    notification_service = NotificationService(db)
    discrepancies = notification_service.check_discrepancy(project_id=project_id)
    
    return success_response(
        data=discrepancies,
        message="Discrepancy check berhasil"
    )


# ========== NOTIFICATION ROUTES ==========
@router.get(
    "/notifications",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get notifications",
    tags=["Notifications"]
)
async def get_notifications(
    is_read: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get notifications"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    skip = (page - 1) * limit
    notification_service = NotificationService(db)
    notifications, total = notification_service.get_notifications(
        is_read=is_read,
        skip=skip,
        limit=limit,
        project_id=project_id
    )
    
    # Add mandor and material names
    result = []
    for notif in notifications:
        notif_dict = NotificationResponse.model_validate(notif).model_dump(mode="json")
        # Get related data
        mandor = notification_service.mandor_repo.get(notif.mandor_id)
        material = notification_service.material_repo.get(notif.material_id)
        notif_dict["mandor_nama"] = mandor.nama if mandor else None
        notif_dict["material_nama"] = material.nama_barang if material else None
        result.append(notif_dict)
    
    return paginated_response(
        data=result,
        total=total,
        page=page,
        limit=limit,
        message="Daftar notifications berhasil diambil"
    )


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    tags=["Notifications"]
)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Mark notification as read"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    notification_service = NotificationService(db)
    notification_service.mark_as_read(notification_id)
    
    return success_response(
        message="Notification berhasil ditandai sebagai sudah dibaca"
    )


# ========== EXPORT EXCEL ROUTES ==========
@router.post(
    "/export-excel",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Export to Excel",
    tags=["Export"]
)
async def export_excel(
    export_data: ExportExcelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Export data to Excel"""
    try:
        check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
        
        excel_file = create_excel_export(
            db=db,
            start_date=export_data.start_date,
            end_date=export_data.end_date,
            mandor_id=export_data.mandor_id,
            material_id=export_data.material_id,
            search=export_data.search
        )
        
        # Get file content before closing
        file_content = excel_file.read()
        excel_file.close()
        
        # Audit log
        try:
            audit_service = AuditLogService(db)
            audit_service.create_log(
                user_id=current_user.id,
                action=ActionType.EXPORT,
                table_name="inventory",
                description=f"Export Excel - Date: {export_data.start_date} to {export_data.end_date}"
            )
        except Exception as audit_error:
            logger.warning(f"Failed to create audit log: {audit_error}")
        
        from datetime import datetime
        filename = f"laporan_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return Response(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        logger.error(f"Error exporting Excel: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal export Excel: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== SURAT PERMINTAAN ROUTES ==========
@router.post(
    "/surat-permintaan",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create surat permintaan",
    tags=["Surat Permintaan"]
)
async def create_surat_permintaan(
    surat_permintaan_data: SuratPermintaanCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create surat permintaan dengan auto-generate nomor surat"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_permintaan_service = SuratPermintaanService(db)
        
        # Convert items to dict format
        items = []
        for item in surat_permintaan_data.items:
            # Convert Decimal qty to float if needed (already handled by Pydantic, but ensure consistency)
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            items.append({
                "material_id": item.material_id,
                "kode_barang": item.kode_barang,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "satuan": item.satuan,
                "sumber_barang": item.sumber_barang,
                "peruntukan": item.peruntukan
            })
        
        # Create surat permintaan
        surat_permintaan = surat_permintaan_service.create(
            tanggal=surat_permintaan_data.tanggal,
            items=items,
            signatures=surat_permintaan_data.signatures,
            created_by=current_user.id,
            project_id=project_id
        )
        
        # Load items with relationships
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_permintaan import SuratPermintaan
        from app.models.inventory.surat_permintaan_item import SuratPermintaanItem
        
        sp_full = db.query(SuratPermintaan).options(
            joinedload(SuratPermintaan.items).joinedload(SuratPermintaanItem.material),
            joinedload(SuratPermintaan.project),
            joinedload(SuratPermintaan.creator)
        ).filter(SuratPermintaan.id == surat_permintaan.id).first()
        
        if not sp_full:
            return error_response(
                message="Surat permintaan tidak ditemukan setelah dibuat",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Build response data manually
        response_data = {
            "id": sp_full.id,
            "nomor_surat": sp_full.nomor_surat,
            "tanggal": sp_full.tanggal.isoformat() if isinstance(sp_full.tanggal, date) else str(sp_full.tanggal),
            "project_id": sp_full.project_id,
            "created_by": sp_full.created_by,
            "created_at": sp_full.created_at.isoformat() if isinstance(sp_full.created_at, datetime) else str(sp_full.created_at),
            "updated_at": sp_full.updated_at.isoformat() if isinstance(sp_full.updated_at, datetime) else str(sp_full.updated_at),
            "items": []
        }
        
        # Parse signatures JSON
        if sp_full.signatures:
            try:
                response_data["signatures"] = json.loads(sp_full.signatures) if isinstance(sp_full.signatures, str) else sp_full.signatures
            except:
                response_data["signatures"] = None
        else:
            response_data["signatures"] = None
        
        # Build items
        for item in sp_full.items:
            # Convert Decimal/Numeric qty to float to preserve decimal precision in JSON
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            item_data = {
                "id": item.id,
                "material_id": item.material_id,
                "kode_barang": item.kode_barang,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "satuan": item.satuan,
                "material": None
            }
            
            # Parse sumber_barang JSON
            if item.sumber_barang:
                try:
                    item_data["sumber_barang"] = json.loads(item.sumber_barang) if isinstance(item.sumber_barang, str) else item.sumber_barang
                except:
                    item_data["sumber_barang"] = None
            else:
                item_data["sumber_barang"] = None
            
            # Parse peruntukan JSON
            if item.peruntukan:
                try:
                    item_data["peruntukan"] = json.loads(item.peruntukan) if isinstance(item.peruntukan, str) else item.peruntukan
                except:
                    item_data["peruntukan"] = None
            else:
                item_data["peruntukan"] = None
            
            # Add material if exists
            if item.material:
                item_data["material"] = {
                    "id": item.material.id,
                    "kode_barang": item.material.kode_barang,
                    "nama_barang": item.material.nama_barang,
                    "satuan": item.material.satuan
                }
            
            response_data["items"].append(item_data)
        
        # Add project if exists
        if sp_full.project:
            response_data["project"] = {
                "id": sp_full.project.id,
                "name": sp_full.project.name,
                "code": sp_full.project.code
            }
        else:
            response_data["project"] = None
        
        # Add creator if exists
        if sp_full.creator:
            response_data["creator"] = {
                "id": sp_full.creator.id,
                "name": sp_full.creator.name,
                "email": sp_full.creator.email
            }
        else:
            response_data["creator"] = None
        
        return success_response(
            data=response_data,
            message=f"Surat permintaan {surat_permintaan.nomor_surat} berhasil dibuat"
        )
    except Exception as e:
        logger.error(f"Error creating surat permintaan: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal membuat surat permintaan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get(
    "/surat-permintaan",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get list surat permintaan",
    tags=["Surat Permintaan"]
)
async def get_surat_permintaans(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get list surat permintaan dengan pagination"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_permintaan_service = SuratPermintaanService(db)
        skip = (page - 1) * limit
        
        surat_permintaans, total = surat_permintaan_service.get_all(
            skip=skip,
            limit=limit,
            search=search,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            user_id=current_user.id
        )
        
        # Convert to response format
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_permintaan import SuratPermintaan
        from app.models.inventory.surat_permintaan_item import SuratPermintaanItem
        
        response_items = []
        for sp in surat_permintaans:
            # Load with relationships
            sp_full = db.query(SuratPermintaan).options(
                joinedload(SuratPermintaan.items).joinedload(SuratPermintaanItem.material),
                joinedload(SuratPermintaan.project),
                joinedload(SuratPermintaan.creator)
            ).filter(SuratPermintaan.id == sp.id).first()
            
            if sp_full:
                # Build response data manually
                item_data = {
                    "id": sp_full.id,
                    "nomor_surat": sp_full.nomor_surat,
                    "tanggal": sp_full.tanggal.isoformat() if isinstance(sp_full.tanggal, date) else str(sp_full.tanggal),
                    "project_id": sp_full.project_id,
                    "status": getattr(sp_full, 'status', 'Draft'),
                    "created_by": sp_full.created_by,
                    "created_at": sp_full.created_at.isoformat() if isinstance(sp_full.created_at, datetime) else str(sp_full.created_at),
                    "updated_at": sp_full.updated_at.isoformat() if isinstance(sp_full.updated_at, datetime) else str(sp_full.updated_at),
                    "items": []
                }
                
                # Parse signatures JSON
                if sp_full.signatures:
                    try:
                        item_data["signatures"] = json.loads(sp_full.signatures) if isinstance(sp_full.signatures, str) else sp_full.signatures
                    except:
                        item_data["signatures"] = None
                else:
                    item_data["signatures"] = None
                
                # Build items
                for item in sp_full.items:
                    # Convert Decimal/Numeric qty to float to preserve decimal precision in JSON
                    qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
                    
                    item_dict = {
                        "id": item.id,
                        "material_id": item.material_id,
                        "kode_barang": item.kode_barang,
                        "nama_barang": item.nama_barang,
                        "qty": qty_value,
                        "satuan": item.satuan,
                        "material": None
                    }
                    
                    # Parse sumber_barang JSON
                    if item.sumber_barang:
                        try:
                            item_dict["sumber_barang"] = json.loads(item.sumber_barang) if isinstance(item.sumber_barang, str) else item.sumber_barang
                        except:
                            item_dict["sumber_barang"] = None
                    else:
                        item_dict["sumber_barang"] = None
                    
                    # Parse peruntukan JSON
                    if item.peruntukan:
                        try:
                            item_dict["peruntukan"] = json.loads(item.peruntukan) if isinstance(item.peruntukan, str) else item.peruntukan
                        except:
                            item_dict["peruntukan"] = None
                    else:
                        item_dict["peruntukan"] = None
                    
                    # Add material if exists
                    if item.material:
                        item_dict["material"] = {
                            "id": item.material.id,
                            "kode_barang": item.material.kode_barang,
                            "nama_barang": item.material.nama_barang,
                            "satuan": item.material.satuan
                        }
                    
                    item_data["items"].append(item_dict)
                
                # Add project if exists
                if sp_full.project:
                    item_data["project"] = {
                        "id": sp_full.project.id,
                        "name": sp_full.project.name,
                        "code": sp_full.project.code
                    }
                else:
                    item_data["project"] = None
                
                # Add creator if exists
                if sp_full.creator:
                    item_data["creator"] = {
                        "id": sp_full.creator.id,
                        "name": sp_full.creator.name,
                        "email": sp_full.creator.email
                    }
                else:
                    item_data["creator"] = None
                
                response_items.append(item_data)
        
        return paginated_response(
            data=response_items,
            total=total,
            page=page,
            limit=limit,
            message="Daftar surat permintaan berhasil diambil"
        )
    except Exception as e:
        logger.error(f"Error getting surat permintaans: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal mengambil daftar surat permintaan: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/surat-permintaan/{surat_permintaan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get surat permintaan by ID",
    tags=["Surat Permintaan"]
)
async def get_surat_permintaan(
    surat_permintaan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get surat permintaan by ID"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_permintaan_service = SuratPermintaanService(db)
        surat_permintaan = surat_permintaan_service.get_by_id(surat_permintaan_id, project_id=project_id)
        
        if not surat_permintaan:
            return error_response(
                message="Surat permintaan tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Load with relationships
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_permintaan import SuratPermintaan
        from app.models.inventory.surat_permintaan_item import SuratPermintaanItem
        
        sp_full = db.query(SuratPermintaan).options(
            joinedload(SuratPermintaan.items).joinedload(SuratPermintaanItem.material),
            joinedload(SuratPermintaan.project),
            joinedload(SuratPermintaan.creator)
        ).filter(SuratPermintaan.id == surat_permintaan_id).first()
        
        if not sp_full:
            return error_response(
                message="Surat permintaan tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Build response data manually
        response_data = {
            "id": sp_full.id,
            "nomor_surat": sp_full.nomor_surat,
            "tanggal": sp_full.tanggal.isoformat() if isinstance(sp_full.tanggal, date) else str(sp_full.tanggal),
            "project_id": sp_full.project_id,
            "created_by": sp_full.created_by,
            "created_at": sp_full.created_at.isoformat() if isinstance(sp_full.created_at, datetime) else str(sp_full.created_at),
            "updated_at": sp_full.updated_at.isoformat() if isinstance(sp_full.updated_at, datetime) else str(sp_full.updated_at),
            "items": []
        }
        
        # Parse signatures JSON
        if sp_full.signatures:
            try:
                response_data["signatures"] = json.loads(sp_full.signatures) if isinstance(sp_full.signatures, str) else sp_full.signatures
            except:
                response_data["signatures"] = None
        else:
            response_data["signatures"] = None
        
        # Build items
        for item in sp_full.items:
            # Convert Decimal/Numeric qty to float to preserve decimal precision in JSON
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            item_data = {
                "id": item.id,
                "material_id": item.material_id,
                "kode_barang": item.kode_barang,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "satuan": item.satuan,
                "material": None
            }
            
            # Parse sumber_barang JSON
            if item.sumber_barang:
                try:
                    item_data["sumber_barang"] = json.loads(item.sumber_barang) if isinstance(item.sumber_barang, str) else item.sumber_barang
                except:
                    item_data["sumber_barang"] = None
            else:
                item_data["sumber_barang"] = None
            
            # Parse peruntukan JSON
            if item.peruntukan:
                try:
                    item_data["peruntukan"] = json.loads(item.peruntukan) if isinstance(item.peruntukan, str) else item.peruntukan
                except:
                    item_data["peruntukan"] = None
            else:
                item_data["peruntukan"] = None
            
            # Add material if exists
            if item.material:
                item_data["material"] = {
                    "id": item.material.id,
                    "kode_barang": item.material.kode_barang,
                    "nama_barang": item.material.nama_barang,
                    "satuan": item.material.satuan
                }
            
            response_data["items"].append(item_data)
        
        # Add project if exists
        if sp_full.project:
            response_data["project"] = {
                "id": sp_full.project.id,
                "name": sp_full.project.name,
                "code": sp_full.project.code
            }
        else:
            response_data["project"] = None
        
        # Add creator if exists
        if sp_full.creator:
            response_data["creator"] = {
                "id": sp_full.creator.id,
                "name": sp_full.creator.name,
                "email": sp_full.creator.email
            }
        else:
            response_data["creator"] = None
        
        return success_response(
            data=response_data,
            message="Surat permintaan berhasil diambil"
        )
    except Exception as e:
        logger.error(f"Error getting surat permintaan: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal mengambil surat permintaan: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/surat-permintaan/by-nomor/{nomor_surat}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get surat permintaan by nomor surat",
    tags=["Surat Permintaan"]
)
async def get_surat_permintaan_by_nomor(
    nomor_surat: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get surat permintaan by nomor surat"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_permintaan_service = SuratPermintaanService(db)
        surat_permintaan = surat_permintaan_service.get_by_nomor_surat(nomor_surat, project_id=project_id)
        
        if not surat_permintaan:
            return error_response(
                message="Surat permintaan tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Load with relationships
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_permintaan import SuratPermintaan
        from app.models.inventory.surat_permintaan_item import SuratPermintaanItem
        
        sp_full = db.query(SuratPermintaan).options(
            joinedload(SuratPermintaan.items).joinedload(SuratPermintaanItem.material),
            joinedload(SuratPermintaan.project),
            joinedload(SuratPermintaan.creator)
        ).filter(SuratPermintaan.nomor_surat == nomor_surat).first()
        
        if not sp_full:
            return error_response(
                message="Surat permintaan tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Build response data manually
        response_data = {
            "id": sp_full.id,
            "nomor_surat": sp_full.nomor_surat,
            "tanggal": sp_full.tanggal.isoformat() if isinstance(sp_full.tanggal, date) else str(sp_full.tanggal),
            "project_id": sp_full.project_id,
            "status": getattr(sp_full, 'status', 'Draft'),
            "created_by": sp_full.created_by,
            "created_at": sp_full.created_at.isoformat() if isinstance(sp_full.created_at, datetime) else str(sp_full.created_at),
            "updated_at": sp_full.updated_at.isoformat() if isinstance(sp_full.updated_at, datetime) else str(sp_full.updated_at),
            "items": []
        }
        
        # Parse signatures JSON
        if sp_full.signatures:
            try:
                response_data["signatures"] = json.loads(sp_full.signatures) if isinstance(sp_full.signatures, str) else sp_full.signatures
            except:
                response_data["signatures"] = None
        else:
            response_data["signatures"] = None
        
        # Build items
        for item in sp_full.items:
            # Convert Decimal/Numeric qty to float to preserve decimal precision in JSON
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            item_data = {
                "id": item.id,
                "material_id": item.material_id,
                "kode_barang": item.kode_barang,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "satuan": item.satuan,
                "material": None
            }
            
            # Parse sumber_barang JSON
            if item.sumber_barang:
                try:
                    item_data["sumber_barang"] = json.loads(item.sumber_barang) if isinstance(item.sumber_barang, str) else item.sumber_barang
                except:
                    item_data["sumber_barang"] = None
            else:
                item_data["sumber_barang"] = None
            
            # Parse peruntukan JSON
            if item.peruntukan:
                try:
                    item_data["peruntukan"] = json.loads(item.peruntukan) if isinstance(item.peruntukan, str) else item.peruntukan
                except:
                    item_data["peruntukan"] = None
            else:
                item_data["peruntukan"] = None
            
            # Add material if exists
            if item.material:
                item_data["material"] = {
                    "id": item.material.id,
                    "kode_barang": item.material.kode_barang,
                    "nama_barang": item.material.nama_barang,
                    "satuan": item.material.satuan
                }
            
            response_data["items"].append(item_data)
        
        # Add project if exists
        if sp_full.project:
            response_data["project"] = {
                "id": sp_full.project.id,
                "name": sp_full.project.name,
                "code": sp_full.project.code
            }
        else:
            response_data["project"] = None
        
        # Add creator if exists
        if sp_full.creator:
            response_data["creator"] = {
                "id": sp_full.creator.id,
                "name": sp_full.creator.name,
                "email": sp_full.creator.email
            }
        else:
            response_data["creator"] = None
        
        return success_response(
            data=response_data,
            message="Surat permintaan berhasil diambil"
        )
    except Exception as e:
        logger.error(f"Error getting surat permintaan by nomor: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal mengambil surat permintaan: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== SURAT JALAN ROUTES ==========
@router.post(
    "/surat-jalan",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create surat jalan",
    tags=["Surat Jalan"]
)
async def create_surat_jalan(
    surat_jalan_data: SuratJalanCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Create surat jalan dengan auto-generate nomor form"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_jalan_service = SuratJalanService(db)
        
        # Convert items to dict format
        items = []
        for item in surat_jalan_data.items:
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            items.append({
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "keterangan": item.keterangan
            })
        
        # Create surat jalan
        surat_jalan = surat_jalan_service.create(
            kepada=surat_jalan_data.kepada,
            tanggal_pengiriman=surat_jalan_data.tanggal_pengiriman,
            items=items,
            nama_pemberi=surat_jalan_data.nama_pemberi,
            nama_penerima=surat_jalan_data.nama_penerima,
            tanggal_diterima=surat_jalan_data.tanggal_diterima,
            created_by=current_user.id,
            project_id=project_id,
            nomor_surat_permintaan=surat_jalan_data.nomor_surat_permintaan,
            nomor_barang_keluar=surat_jalan_data.nomor_barang_keluar
        )
        
        # Load items with relationships
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_jalan import SuratJalan
        from app.models.inventory.surat_jalan_item import SuratJalanItem
        
        sj_full = db.query(SuratJalan).options(
            joinedload(SuratJalan.items),
            joinedload(SuratJalan.project),
            joinedload(SuratJalan.creator)
        ).filter(SuratJalan.id == surat_jalan.id).first()
        
        if not sj_full:
            return error_response(
                message="Surat jalan tidak ditemukan setelah dibuat",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Build response data manually
        response_data = {
            "id": sj_full.id,
            "nomor_form": sj_full.nomor_form,
            "kepada": sj_full.kepada,
            "tanggal_pengiriman": sj_full.tanggal_pengiriman.isoformat() if isinstance(sj_full.tanggal_pengiriman, date) else str(sj_full.tanggal_pengiriman),
            "nama_pemberi": sj_full.nama_pemberi,
            "nama_penerima": sj_full.nama_penerima,
            "tanggal_diterima": sj_full.tanggal_diterima.isoformat() if sj_full.tanggal_diterima and isinstance(sj_full.tanggal_diterima, date) else (str(sj_full.tanggal_diterima) if sj_full.tanggal_diterima else None),
            "nomor_surat_permintaan": getattr(sj_full, 'nomor_surat_permintaan', None),
            "nomor_barang_keluar": getattr(sj_full, 'nomor_barang_keluar', None),
            "stock_out_id": getattr(sj_full, 'stock_out_id', None),
            "project_id": sj_full.project_id,
            "created_by": sj_full.created_by,
            "created_at": sj_full.created_at.isoformat() if isinstance(sj_full.created_at, datetime) else str(sj_full.created_at),
            "updated_at": sj_full.updated_at.isoformat() if isinstance(sj_full.updated_at, datetime) else str(sj_full.updated_at),
            "items": []
        }
        
        # Build items
        for item in sj_full.items:
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            item_data = {
                "id": item.id,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "keterangan": item.keterangan
            }
            
            response_data["items"].append(item_data)
        
        # Add project if exists
        if sj_full.project:
            response_data["project"] = {
                "id": sj_full.project.id,
                "name": sj_full.project.name,
                "code": sj_full.project.code
            }
        else:
            response_data["project"] = None
        
        # Add creator if exists
        if sj_full.creator:
            response_data["creator"] = {
                "id": sj_full.creator.id,
                "name": sj_full.creator.name,
                "email": sj_full.creator.email
            }
        else:
            response_data["creator"] = None
        
        return success_response(
            data=response_data,
            message=f"Surat jalan {surat_jalan.nomor_form} berhasil dibuat"
        )
    except Exception as e:
        logger.error(f"Error creating surat jalan: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal membuat surat jalan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get(
    "/surat-jalan",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get list surat jalan",
    tags=["Surat Jalan"]
)
async def get_surat_jalans(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get list surat jalan dengan pagination"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_jalan_service = SuratJalanService(db)
        skip = (page - 1) * limit
        
        surat_jalans, total = surat_jalan_service.get_all(
            skip=skip,
            limit=limit,
            search=search,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            user_id=current_user.id
        )
        
        # Convert to response format
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_jalan import SuratJalan
        from app.models.inventory.surat_jalan_item import SuratJalanItem
        
        response_items = []
        for sj in surat_jalans:
            # Load with relationships
            sj_full = db.query(SuratJalan).options(
                joinedload(SuratJalan.items),
                joinedload(SuratJalan.project),
                joinedload(SuratJalan.creator)
            ).filter(SuratJalan.id == sj.id).first()
            
            if sj_full:
                # Build response data manually
                item_data = {
                    "id": sj_full.id,
                    "nomor_form": sj_full.nomor_form,
                    "kepada": sj_full.kepada,
                    "tanggal_pengiriman": sj_full.tanggal_pengiriman.isoformat() if isinstance(sj_full.tanggal_pengiriman, date) else str(sj_full.tanggal_pengiriman),
                    "nama_pemberi": sj_full.nama_pemberi,
                    "nama_penerima": sj_full.nama_penerima,
                    "tanggal_diterima": sj_full.tanggal_diterima.isoformat() if sj_full.tanggal_diterima and isinstance(sj_full.tanggal_diterima, date) else (str(sj_full.tanggal_diterima) if sj_full.tanggal_diterima else None),
                    "nomor_surat_permintaan": getattr(sj_full, 'nomor_surat_permintaan', None),
                    "project_id": sj_full.project_id,
                    "created_by": sj_full.created_by,
                    "created_at": sj_full.created_at.isoformat() if isinstance(sj_full.created_at, datetime) else str(sj_full.created_at),
                    "updated_at": sj_full.updated_at.isoformat() if isinstance(sj_full.updated_at, datetime) else str(sj_full.updated_at),
                    "items": []
                }
                
                # Build items
                for item in sj_full.items:
                    qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
                    
                    item_data_item = {
                        "id": item.id,
                        "nama_barang": item.nama_barang,
                        "qty": qty_value,
                        "keterangan": item.keterangan
                    }
                    
                    item_data["items"].append(item_data_item)
                
                # Add project if exists
                if sj_full.project:
                    item_data["project"] = {
                        "id": sj_full.project.id,
                        "name": sj_full.project.name,
                        "code": sj_full.project.code
                    }
                else:
                    item_data["project"] = None
                
                # Add creator if exists
                if sj_full.creator:
                    item_data["creator"] = {
                        "id": sj_full.creator.id,
                        "name": sj_full.creator.name,
                        "email": sj_full.creator.email
                    }
                else:
                    item_data["creator"] = None
                
                response_items.append(item_data)
        
        return paginated_response(
            data=response_items,
            total=total,
            page=page,
            limit=limit,
            message="Daftar surat jalan berhasil diambil"
        )
    except Exception as e:
        logger.error(f"Error getting surat jalans: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal mengambil daftar surat jalan: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/surat-jalan/{surat_jalan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get surat jalan by ID",
    tags=["Surat Jalan"]
)
async def get_surat_jalan_by_id(
    surat_jalan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Get surat jalan by ID"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_jalan_service = SuratJalanService(db)
        surat_jalan = surat_jalan_service.get_by_id(surat_jalan_id, project_id=project_id)
        
        if not surat_jalan:
            return error_response(
                message="Surat jalan tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Load with relationships
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_jalan import SuratJalan
        from app.models.inventory.surat_jalan_item import SuratJalanItem
        
        sj_full = db.query(SuratJalan).options(
            joinedload(SuratJalan.items),
            joinedload(SuratJalan.project),
            joinedload(SuratJalan.creator)
        ).filter(SuratJalan.id == surat_jalan_id).first()
        
        if not sj_full:
            return error_response(
                message="Surat jalan tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Build response data manually
        response_data = {
            "id": sj_full.id,
            "nomor_form": sj_full.nomor_form,
            "kepada": sj_full.kepada,
            "tanggal_pengiriman": sj_full.tanggal_pengiriman.isoformat() if isinstance(sj_full.tanggal_pengiriman, date) else str(sj_full.tanggal_pengiriman),
            "nama_pemberi": sj_full.nama_pemberi,
            "nama_penerima": sj_full.nama_penerima,
            "tanggal_diterima": sj_full.tanggal_diterima.isoformat() if sj_full.tanggal_diterima and isinstance(sj_full.tanggal_diterima, date) else (str(sj_full.tanggal_diterima) if sj_full.tanggal_diterima else None),
            "project_id": sj_full.project_id,
            "created_by": sj_full.created_by,
            "created_at": sj_full.created_at.isoformat() if isinstance(sj_full.created_at, datetime) else str(sj_full.created_at),
            "updated_at": sj_full.updated_at.isoformat() if isinstance(sj_full.updated_at, datetime) else str(sj_full.updated_at),
            "items": []
        }
        
        # Build items
        for item in sj_full.items:
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            item_data = {
                "id": item.id,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "keterangan": item.keterangan
            }
            
            response_data["items"].append(item_data)
        
        # Add project if exists
        if sj_full.project:
            response_data["project"] = {
                "id": sj_full.project.id,
                "name": sj_full.project.name,
                "code": sj_full.project.code
            }
        else:
            response_data["project"] = None
        
        # Add creator if exists
        if sj_full.creator:
            response_data["creator"] = {
                "id": sj_full.creator.id,
                "name": sj_full.creator.name,
                "email": sj_full.creator.email
            }
        else:
            response_data["creator"] = None
        
        return success_response(
            data=response_data,
            message="Surat jalan berhasil diambil"
        )
    except Exception as e:
        logger.error(f"Error getting surat jalan by ID: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal mengambil surat jalan: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put(
    "/surat-jalan/{surat_jalan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update surat jalan",
    tags=["Surat Jalan"]
)
async def update_surat_jalan(
    surat_jalan_id: int,
    surat_jalan_data: SuratJalanUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Update surat jalan"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_jalan_service = SuratJalanService(db)
        
        # Convert items to dict format if provided
        items = None
        if surat_jalan_data.items:
            items = []
            for item in surat_jalan_data.items:
                qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
                
                items.append({
                    "nama_barang": item.nama_barang,
                    "qty": qty_value,
                    "keterangan": item.keterangan
                })
        
        # Update surat jalan
        surat_jalan = surat_jalan_service.update(
            id=surat_jalan_id,
            kepada=surat_jalan_data.kepada,
            tanggal_pengiriman=surat_jalan_data.tanggal_pengiriman,
            items=items,
            nama_pemberi=surat_jalan_data.nama_pemberi,
            nama_penerima=surat_jalan_data.nama_penerima,
            tanggal_diterima=surat_jalan_data.tanggal_diterima,
            updated_by=current_user.id,
            project_id=project_id
        )
        
        # Load with relationships
        from sqlalchemy.orm import joinedload
        from app.models.inventory.surat_jalan import SuratJalan
        from app.models.inventory.surat_jalan_item import SuratJalanItem
        
        sj_full = db.query(SuratJalan).options(
            joinedload(SuratJalan.items),
            joinedload(SuratJalan.project),
            joinedload(SuratJalan.creator)
        ).filter(SuratJalan.id == surat_jalan.id).first()
        
        if not sj_full:
            return error_response(
                message="Surat jalan tidak ditemukan setelah diupdate",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Build response data manually
        response_data = {
            "id": sj_full.id,
            "nomor_form": sj_full.nomor_form,
            "kepada": sj_full.kepada,
            "tanggal_pengiriman": sj_full.tanggal_pengiriman.isoformat() if isinstance(sj_full.tanggal_pengiriman, date) else str(sj_full.tanggal_pengiriman),
            "nama_pemberi": sj_full.nama_pemberi,
            "nama_penerima": sj_full.nama_penerima,
            "tanggal_diterima": sj_full.tanggal_diterima.isoformat() if sj_full.tanggal_diterima and isinstance(sj_full.tanggal_diterima, date) else (str(sj_full.tanggal_diterima) if sj_full.tanggal_diterima else None),
            "project_id": sj_full.project_id,
            "created_by": sj_full.created_by,
            "created_at": sj_full.created_at.isoformat() if isinstance(sj_full.created_at, datetime) else str(sj_full.created_at),
            "updated_at": sj_full.updated_at.isoformat() if isinstance(sj_full.updated_at, datetime) else str(sj_full.updated_at),
            "items": []
        }
        
        # Build items
        for item in sj_full.items:
            qty_value = float(item.qty) if isinstance(item.qty, Decimal) else item.qty
            
            item_data = {
                "id": item.id,
                "nama_barang": item.nama_barang,
                "qty": qty_value,
                "keterangan": item.keterangan
            }
            
            response_data["items"].append(item_data)
        
        # Add project if exists
        if sj_full.project:
            response_data["project"] = {
                "id": sj_full.project.id,
                "name": sj_full.project.name,
                "code": sj_full.project.code
            }
        else:
            response_data["project"] = None
        
        # Add creator if exists
        if sj_full.creator:
            response_data["creator"] = {
                "id": sj_full.creator.id,
                "name": sj_full.creator.name,
                "email": sj_full.creator.email
            }
        else:
            response_data["creator"] = None
        
        return success_response(
            data=response_data,
            message=f"Surat jalan {surat_jalan.nomor_form} berhasil diupdate"
        )
    except Exception as e:
        logger.error(f"Error updating surat jalan: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal mengupdate surat jalan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.delete(
    "/surat-jalan/{surat_jalan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Delete surat jalan",
    tags=["Surat Jalan"]
)
async def delete_surat_jalan(
    surat_jalan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Depends(get_current_project)
):
    """Soft delete surat jalan"""
    check_role_permission(current_user, [UserRole.ADMIN, UserRole.GUDANG])
    
    try:
        surat_jalan_service = SuratJalanService(db)
        surat_jalan_service.soft_delete(surat_jalan_id, current_user.id, project_id=project_id)
        
        return success_response(
            data=None,
            message="Surat jalan berhasil dihapus"
        )
    except Exception as e:
        logger.error(f"Error deleting surat jalan: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal menghapus surat jalan: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

