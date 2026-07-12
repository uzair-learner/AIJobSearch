from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CurrentJob, DataImport, Employer, PermCase
from app.services.current_job_service import CurrentJobService

router = APIRouter(tags=["health"])
current_job_service = CurrentJobService()


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "employers": db.scalar(select(func.count()).select_from(Employer)),
            "permCases": db.scalar(select(func.count()).select_from(PermCase)),
            "currentJobs": db.scalar(select(func.count()).select_from(CurrentJob)),
        },
        "imports": {
            "lastStatus": db.scalar(select(DataImport.status).order_by(DataImport.started_at.desc()).limit(1)),
            "lastCompletedAt": db.scalar(select(DataImport.completed_at).order_by(DataImport.completed_at.desc()).limit(1)),
        },
        "nextCurrentJobsRefresh": current_job_service.next_refresh_at(180),
    }
