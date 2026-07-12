from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search import SponsorSearchRequest
from app.services.sponsor_search_service import SponsorSearchService
from app.utils.security import enforce_rate_limit

router = APIRouter(prefix="/sponsors", tags=["sponsors"])
service = SponsorSearchService()


@router.post("/search")
def sponsor_search(payload: SponsorSearchRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request)
    return service.search(db, payload).model_dump()
