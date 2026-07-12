from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search import CurrentJobSearchRequest
from app.services.current_job_service import CurrentJobService
from app.utils.security import enforce_rate_limit

router = APIRouter(prefix="/jobs", tags=["jobs"])
service = CurrentJobService()


@router.post("/search")
def current_job_search(payload: CurrentJobSearchRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request)
    return service.search_jobs(db, payload).model_dump()
