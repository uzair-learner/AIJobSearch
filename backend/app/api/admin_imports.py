from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.importers.perm_importer import PermImporter
from app.models import DataImport
from app.schemas.import_schema import DataImportResponse, ImportFromSourceRequest
from app.utils.checksum import file_checksum
from app.utils.file_validator import validate_upload
from app.utils.security import verify_admin_token

router = APIRouter(prefix="/admin/imports", tags=["admin-imports"], dependencies=[Depends(verify_admin_token)])
settings = get_settings()
importer = PermImporter()


def _serialize(record: DataImport) -> DataImportResponse:
    return DataImportResponse(
        id=record.id,
        sourceName=record.source_name,
        sourceUrl=record.source_url,
        fiscalYear=record.fiscal_year,
        reportingPeriod=record.reporting_period,
        fileName=record.file_name,
        fileHash=record.file_hash,
        status=record.status,
        recordsProcessed=record.records_processed,
        recordsInserted=record.records_inserted,
        recordsUpdated=record.records_updated,
        recordsRejected=record.records_rejected,
        startedAt=record.started_at.isoformat(),
        completedAt=record.completed_at.isoformat() if record.completed_at else None,
        errorMessage=record.error_message,
    )


@router.post("/perm/upload")
async def upload_perm_file(
    fiscalYear: int,
    reportingPeriod: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    validate_upload(file, settings.max_upload_size_mb * 1024 * 1024)
    content = await file.read()
    try:
        record = importer.import_bytes(
            db,
            file_name=file.filename or "upload.csv",
            content=content,
            fiscal_year=fiscalYear,
            reporting_period=reportingPeriod,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _serialize(record).model_dump()


@router.post("/perm/from-source")
def import_from_source(payload: ImportFromSourceRequest, db: Session = Depends(get_db)) -> dict:
    host_allowed = any(payload.sourceUrl.startswith(f"https://{host}") for host in settings.approved_download_hosts)
    if not host_allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source URL is not approved.")
    record = DataImport(
        source_name="OFLC PERM",
        source_url=payload.sourceUrl,
        fiscal_year=payload.fiscalYear,
        reporting_period=payload.reportingPeriod,
        file_name="remote-source",
        file_hash=file_checksum(payload.sourceUrl.encode("utf-8")),
        status="pending",
        started_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record).model_dump()


@router.get("")
def list_imports(db: Session = Depends(get_db)) -> list[dict]:
    records = db.scalars(select(DataImport).order_by(DataImport.started_at.desc())).all()
    return [_serialize(record).model_dump() for record in records]


@router.get("/{importId}")
def get_import(importId: int, db: Session = Depends(get_db)) -> dict:
    record = db.get(DataImport, importId)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import not found.")
    return _serialize(record).model_dump()


@router.post("/{importId}/retry")
def retry_import(importId: int, db: Session = Depends(get_db)) -> dict:
    record = db.get(DataImport, importId)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import not found.")
    record.status = "pending_retry"
    record.error_message = None
    db.commit()
    db.refresh(record)
    return _serialize(record).model_dump()
