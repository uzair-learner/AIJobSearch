from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CurrentJob, DataImport, Occupation, PermCase
from app.services.occupation_service import OccupationService

router = APIRouter(prefix="/metadata", tags=["metadata"])
occupation_service = OccupationService()


@router.get("/fiscal-years")
def fiscal_years(db: Session = Depends(get_db)) -> list[dict]:
    years = db.execute(
        select(PermCase.fiscal_year, DataImport.reporting_period)
        .outerjoin(DataImport, DataImport.fiscal_year == PermCase.fiscal_year)
        .distinct()
        .order_by(PermCase.fiscal_year.desc())
    ).all()
    payload = [{"label": "All years", "value": "all", "reportingPeriod": None}]
    for fiscal_year, reporting_period in years:
        payload.append(
            {
                "label": f"FY {fiscal_year}",
                "value": fiscal_year,
                "reportingPeriod": reporting_period or "Complete",
            }
        )
    return payload


@router.get("/it-professions")
def it_professions(db: Session = Depends(get_db)) -> list[dict]:
    return [item.model_dump() for item in occupation_service.list_it_professions(db)]


@router.get("/states")
def states(db: Session = Depends(get_db)) -> list[str]:
    states = db.scalars(select(distinct(PermCase.worksite_state)).order_by(PermCase.worksite_state.asc())).all()
    values = [state for state in states if state]
    return ["All states", *values]


@router.get("/case-statuses")
def case_statuses(db: Session = Depends(get_db)) -> list[str]:
    statuses = db.scalars(select(distinct(PermCase.case_status)).order_by(PermCase.case_status.asc())).all()
    return ["All statuses", *[status for status in statuses if status]]


@router.get("/data-freshness")
def data_freshness(db: Session = Depends(get_db)) -> dict:
    latest_import = db.scalar(select(DataImport).order_by(DataImport.completed_at.desc()).limit(1))
    latest_jobs = db.scalar(select(func.max(CurrentJob.retrieved_at)))
    return {
        "latestGovernmentImport": latest_import.completed_at.isoformat() if latest_import and latest_import.completed_at else None,
        "reportingPeriod": latest_import.reporting_period if latest_import else None,
        "latestCurrentJobsRetrieval": latest_jobs.isoformat() if latest_jobs else None,
        "governmentDataLabel": "Latest imported government data",
    }
