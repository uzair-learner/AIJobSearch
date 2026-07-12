from datetime import date, datetime, timedelta, timezone

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models import CurrentJob, Employer
from app.schemas.search import CurrentJobItem, CurrentJobSearchRequest, CurrentJobSearchResponse

POSITIVE_PHRASES = [
    "green card sponsorship available",
    "permanent residency sponsorship",
    "perm sponsorship",
    "immigration sponsorship available",
    "visa sponsorship available",
    "we sponsor qualified candidates",
    "h-1b sponsorship available",
    "h-1b transfer available",
    "tn candidates accepted",
    "immigration support provided",
    "sponsorship now or in the future is available",
]

NEGATIVE_PHRASES = [
    "no visa sponsorship",
    "sponsorship is not available",
    "unable to sponsor",
    "will not sponsor",
    "cannot sponsor",
    "no current or future sponsorship",
    "does not provide sponsorship now or in the future",
    "must be authorized without sponsorship",
    "must not require sponsorship now or in the future",
    "u.s. citizens only",
    "green-card holders only",
    "permanent work authorization required",
    "no h-1b",
    "no opt",
    "no cpt",
]


class CurrentJobService:
    def classify_sponsorship(self, description: str) -> tuple[str, int, list[str]]:
        lowered = description.lower()
        negative_hits = [phrase for phrase in NEGATIVE_PHRASES if phrase in lowered]
        positive_hits = [phrase for phrase in POSITIVE_PHRASES if phrase in lowered]

        if negative_hits:
            return "sponsorship_unavailable", 0, [f"Negative sponsorship language found: {negative_hits[0]}"]
        if positive_hits:
            return "explicit_sponsorship", 95, [f"Positive sponsorship language found: {positive_hits[0]}"]
        if "sponsor" in lowered or "visa" in lowered or "immigration" in lowered:
            return "may_consider", 60, ["Sponsorship-related language appears without a definitive policy."]
        return "historical_sponsor_policy_unstated", 40, ["No explicit sponsorship language found in the current posting."]

    def search_jobs(self, db: Session, request: CurrentJobSearchRequest) -> CurrentJobSearchResponse:
        query: Select[tuple[CurrentJob]] = select(CurrentJob).options(joinedload(CurrentJob.employer))

        if request.searchText:
            like = f"%{request.searchText.lower()}%"
            query = query.where(
                (CurrentJob.title.ilike(like)) | (CurrentJob.description.ilike(like))
            )
        if request.employerIds:
            query = query.where(CurrentJob.employer_id.in_(request.employerIds))
        if request.professionIds:
            query = query.where(CurrentJob.occupation_id.in_(request.professionIds))
        if request.states:
            query = query.where(CurrentJob.state.in_(request.states))
        if request.sponsorshipClassifications:
            query = query.where(CurrentJob.sponsorship_classification.in_(request.sponsorshipClassifications))
        if request.postedWithinDays:
            cutoff = date.today() - timedelta(days=request.postedWithinDays)
            query = query.where(CurrentJob.posted_date >= cutoff)

        jobs = db.scalars(query.order_by(CurrentJob.posted_date.desc(), CurrentJob.id.desc())).all()
        total = len(jobs)
        start = (request.page - 1) * request.pageSize
        page_jobs = jobs[start : start + request.pageSize]

        items = [
            CurrentJobItem(
                id=job.id,
                employerId=job.employer_id,
                employerName=job.employer.display_name,
                title=job.title,
                source=job.source,
                sourceUrl=job.source_url,
                city=job.city,
                state=job.state,
                remoteType=job.remote_type,
                employmentType=job.employment_type,
                postedDate=job.posted_date.isoformat() if job.posted_date else None,
                sponsorshipClassification=job.sponsorship_classification,
                sponsorshipScore=job.sponsorship_score,
                sponsorshipReasons=[reason for reason in job.sponsorship_reasons.split("||") if reason],
            )
            for job in page_jobs
        ]

        return CurrentJobSearchResponse(
            page=request.page,
            pageSize=request.pageSize,
            totalRecords=total,
            totalPages=max(1, (total + request.pageSize - 1) // request.pageSize),
            results=items,
        )

    def next_refresh_at(self, minutes: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
