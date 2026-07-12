from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employer
from app.services.sponsor_search_service import SponsorSearchService

router = APIRouter(prefix="/employers", tags=["comparisons"])
service = SponsorSearchService()


class CompareRequest(BaseModel):
    employerIds: list[int] = Field(default_factory=list, min_length=1, max_length=5)


@router.post("/compare")
def compare_employers(payload: CompareRequest, db: Session = Depends(get_db)) -> list[dict]:
    items = []
    for employer_id in payload.employerIds:
        employer = db.get(Employer, employer_id)
        if not employer:
            continue
        stats = service.employer_statistics(db, employer_id)
        items.append(
            {
                "employerId": employer.id,
                "employerName": employer.display_name,
                "statistics": stats,
            }
        )
    return items
