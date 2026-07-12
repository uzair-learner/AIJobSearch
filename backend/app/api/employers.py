from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Employer
from app.models.perm_case import PermCase
from app.schemas.employer import (
    EmployerOccupationItem,
    EmployerPermCaseItem,
    EmployerStatisticsResponse,
    EmployerSummaryResponse,
)
from app.services.sponsor_search_service import SponsorSearchService
from app.services.sponsorship_score_service import SponsorshipScoreService

router = APIRouter(prefix="/employers", tags=["employers"])
stats_service = SponsorSearchService()
score_service = SponsorshipScoreService()


def _get_employer(db: Session, employer_id: int) -> Employer:
    employer = (
        db.query(Employer)
        .options(
            selectinload(Employer.perm_cases).selectinload(PermCase.occupation),
            selectinload(Employer.aliases),
            selectinload(Employer.h1b_stats),
            selectinload(Employer.current_jobs),
        )
        .filter(Employer.id == employer_id)
        .first()
    )
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found.")
    return employer


@router.get("/{employerId}")
def employer_details(employerId: int, db: Session = Depends(get_db)) -> dict:
    employer = _get_employer(db, employerId)
    certified = len([case for case in employer.perm_cases if case.case_status.startswith("CERTIFIED")])
    denied = len([case for case in employer.perm_cases if case.case_status == "DENIED"])
    withdrawn = len([case for case in employer.perm_cases if case.case_status == "WITHDRAWN"])
    recent_year = max((case.fiscal_year for case in employer.perm_cases), default=None)
    most_recent_case = max(
        employer.perm_cases,
        key=lambda case: (case.fiscal_year, case.filing_date.isoformat() if case.filing_date else ""),
        default=None,
    )
    current_jobs = [job for job in employer.current_jobs if job.is_active]
    explicit_jobs = [job for job in current_jobs if job.sponsorship_classification == "explicit_sponsorship"]
    score = score_service.calculate(
        recent_certified_filings=certified,
        certified_in_selected_occupation=certified,
        recent_year_count=len({case.fiscal_year for case in employer.perm_cases}),
        has_h1b_history=bool(employer.h1b_stats),
        explicit_job_support_count=len(explicit_jobs),
        explicit_job_denial_count=len([job for job in current_jobs if job.sponsorship_classification == "sponsorship_unavailable"]),
        years_since_recent_activity=(2026 - recent_year) if recent_year else None,
    )
    locations = sorted({f"{case.worksite_city}, {case.worksite_state}" for case in employer.perm_cases if case.worksite_state})
    charts = stats_service.employer_statistics(db, employerId)
    summary = EmployerSummaryResponse(
        id=employer.id,
        employerName=employer.display_name,
        alternateEmployerNames=[alias.alias_name for alias in employer.aliases],
        headquartersOrFilingLocations=locations,
        totalPermFilings=len(employer.perm_cases),
        mostRecentFilingYear=recent_year,
        mostRecentFilingDate=most_recent_case.filing_date.isoformat() if most_recent_case and most_recent_case.filing_date else None,
        certifiedCases=certified,
        deniedCases=denied,
        withdrawnCases=withdrawn,
        certificationRate=round((certified / len(employer.perm_cases)) * 100, 1) if employer.perm_cases else 0,
        numberOfDistinctOccupations=len({case.occupation_id for case in employer.perm_cases if case.occupation_id}),
        numberOfDistinctLocations=len({case.worksite_state for case in employer.perm_cases if case.worksite_state}),
        h1bFilingHistory=[
            {
                "fiscalYear": stat.fiscal_year,
                "initialApprovals": stat.initial_approvals,
                "initialDenials": stat.initial_denials,
                "continuingApprovals": stat.continuing_approvals,
                "continuingDenials": stat.continuing_denials,
            }
            for stat in sorted(employer.h1b_stats, key=lambda stat: stat.fiscal_year, reverse=True)
        ],
        currentJobOpenings=len(current_jobs),
        currentOpeningsMentioningSponsorship=len(explicit_jobs),
        sponsorshipIndicator=score.label,
        sponsorshipScore=score.score,
        sponsorshipReasons=score.reasons,
        dataLimitations=score.limitations,
        charts=charts,
    )
    return summary.model_dump()


@router.get("/{employerId}/perm-cases")
def employer_perm_cases(employerId: int, db: Session = Depends(get_db)) -> list[dict]:
    employer = _get_employer(db, employerId)
    items = [
        EmployerPermCaseItem(
            caseNumber=case.case_number,
            fiscalYear=case.fiscal_year,
            caseStatus=case.case_status,
            filingDate=case.filing_date.isoformat() if case.filing_date else None,
            decisionDate=case.decision_date.isoformat() if case.decision_date else None,
            jobTitle=case.job_title,
            socCode=case.occupation.soc_code if case.occupation else case.original_soc_code,
            socTitle=case.occupation.soc_title if case.occupation else case.original_soc_title,
            worksiteCity=case.worksite_city,
            worksiteState=case.worksite_state,
            offeredWageFrom=case.offered_wage_from,
            wageUnit=case.wage_unit,
            sourceFile=case.source_file,
            sourceUrl=case.source_url,
        )
        for case in sorted(employer.perm_cases, key=lambda item: (item.fiscal_year, item.case_number), reverse=True)
    ]
    return [item.model_dump() for item in items]


@router.get("/{employerId}/occupations")
def employer_occupations(employerId: int, db: Session = Depends(get_db)) -> list[dict]:
    employer = _get_employer(db, employerId)
    counts = Counter(case.occupation_id for case in employer.perm_cases if case.occupation)
    items = [
        EmployerOccupationItem(
            occupationId=case.occupation.id,
            socCode=case.occupation.soc_code,
            socTitle=case.occupation.soc_title,
            professionCategory=case.occupation.profession_category,
            filingCount=counts[case.occupation_id],
        )
        for case in employer.perm_cases
        if case.occupation and counts[case.occupation_id] > 0
    ]
    unique = {item.occupationId: item for item in items}
    return [item.model_dump() for item in unique.values()]


@router.get("/{employerId}/statistics")
def employer_statistics(employerId: int, db: Session = Depends(get_db)) -> dict:
    _get_employer(db, employerId)
    return EmployerStatisticsResponse(**stats_service.employer_statistics(db, employerId)).model_dump()


@router.get("/{employerId}/current-jobs")
def employer_current_jobs(employerId: int, db: Session = Depends(get_db)) -> list[dict]:
    employer = _get_employer(db, employerId)
    return [
        {
            "id": job.id,
            "title": job.title,
            "source": job.source,
            "sourceUrl": job.source_url,
            "city": job.city,
            "state": job.state,
            "postedDate": job.posted_date.isoformat() if job.posted_date else None,
            "sponsorshipClassification": job.sponsorship_classification,
            "sponsorshipScore": job.sponsorship_score,
            "sponsorshipReasons": [reason for reason in job.sponsorship_reasons.split("||") if reason],
        }
        for job in employer.current_jobs
    ]
