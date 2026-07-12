import logging
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CurrentJob, DataImport, Employer, EmployerAlias, H1BEmployerStatistics, Occupation, PermCase
from app.services.current_job_service import CurrentJobService
from app.utils.text_normalizer import normalize_employer_name, normalize_title

logger = logging.getLogger(__name__)


def _get_or_create_employer(db: Session, *, original_name: str, display_name: str, city: str, state: str, website: str) -> Employer:
    normalized_name = normalize_employer_name(original_name)
    employer = db.scalar(select(Employer).where(Employer.normalized_name == normalized_name))
    if employer:
        employer.original_name = original_name
        employer.display_name = display_name
        employer.city = city
        employer.state = state
        employer.website = website
        return employer
    employer = Employer(
        original_name=original_name,
        normalized_name=normalized_name,
        display_name=display_name,
        city=city,
        state=state,
        website=website,
    )
    db.add(employer)
    db.flush()
    return employer


def _get_or_create_alias(db: Session, employer: Employer, alias_name: str, source: str) -> None:
    normalized_alias = normalize_employer_name(alias_name)
    alias = db.scalar(
        select(EmployerAlias).where(
            EmployerAlias.employer_id == employer.id,
            EmployerAlias.normalized_alias == normalized_alias,
        )
    )
    if alias:
        alias.alias_name = alias_name
        alias.source = source
        alias.confidence = 1.0
        alias.manually_verified = True
        return
    db.add(
        EmployerAlias(
            employer_id=employer.id,
            alias_name=alias_name,
            normalized_alias=normalized_alias,
            source=source,
            confidence=1.0,
            manually_verified=True,
        )
    )


def _get_or_create_occupation(db: Session, *, soc_code: str, soc_title: str, profession_category: str) -> Occupation:
    occupation = db.scalar(select(Occupation).where(Occupation.soc_code == soc_code))
    if occupation:
        occupation.soc_title = soc_title
        occupation.profession_category = profession_category
        occupation.normalized_title = normalize_title(soc_title)
        occupation.is_it_profession = True
        occupation.source_year = 2026
        return occupation
    occupation = Occupation(
        soc_code=soc_code,
        soc_title=soc_title,
        profession_category=profession_category,
        normalized_title=normalize_title(soc_title),
        is_it_profession=True,
        source_year=2026,
    )
    db.add(occupation)
    db.flush()
    return occupation


def _get_or_create_perm_case(db: Session, **payload: object) -> None:
    case = db.scalar(select(PermCase).where(PermCase.case_number == payload["case_number"]))
    if case:
        for key, value in payload.items():
            setattr(case, key, value)
        return
    db.add(PermCase(**payload))


def _get_or_create_h1b_stat(db: Session, **payload: object) -> None:
    stat = db.scalar(
        select(H1BEmployerStatistics).where(
            H1BEmployerStatistics.employer_id == payload["employer_id"],
            H1BEmployerStatistics.fiscal_year == payload["fiscal_year"],
        )
    )
    if stat:
        for key, value in payload.items():
            setattr(stat, key, value)
        return
    db.add(H1BEmployerStatistics(**payload))


def _get_or_create_current_job(db: Session, **payload: object) -> None:
    job = db.scalar(select(CurrentJob).where(CurrentJob.external_job_id == payload["external_job_id"]))
    if job:
        for key, value in payload.items():
            setattr(job, key, value)
        return
    db.add(CurrentJob(**payload))


def _get_or_create_import(db: Session, **payload: object) -> None:
    record = db.scalar(select(DataImport).where(DataImport.file_hash == payload["file_hash"]))
    if record:
        for key, value in payload.items():
            setattr(record, key, value)
        return
    db.add(DataImport(**payload))


def seed_demo_data(db: Session) -> None:
    classifier = CurrentJobService()
    try:
        occupations = {
            "software": _get_or_create_occupation(
                db,
                soc_code="15-1252",
                soc_title="Software Developers",
                profession_category="Software development",
            ),
            "data": _get_or_create_occupation(
                db,
                soc_code="15-2051",
                soc_title="Data Scientists",
                profession_category="Data and databases",
            ),
            "security": _get_or_create_occupation(
                db,
                soc_code="15-1212",
                soc_title="Information Security Analysts",
                profession_category="Cybersecurity",
            ),
        }

        employers = {
            "northwind": _get_or_create_employer(
                db,
                original_name="Northwind Cloud Corporation",
                display_name="Northwind Cloud",
                city="Seattle",
                state="WA",
                website="https://example.com/northwind?demo=1",
            ),
            "contoso": _get_or_create_employer(
                db,
                original_name="Contoso Analytics LLC",
                display_name="Contoso Analytics",
                city="Austin",
                state="TX",
                website="https://example.com/contoso?demo=1",
            ),
            "fabrikam": _get_or_create_employer(
                db,
                original_name="Fabrikam Security Inc.",
                display_name="Fabrikam Security",
                city="San Jose",
                state="CA",
                website="https://example.com/fabrikam?demo=1",
            ),
        }

        _get_or_create_alias(db, employers["northwind"], "Northwind Cloud Corporation", "synthetic-demo")
        _get_or_create_alias(db, employers["northwind"], "Northwind", "synthetic-demo")
        _get_or_create_alias(db, employers["contoso"], "Contoso Analytics LLC", "synthetic-demo")
        _get_or_create_alias(db, employers["contoso"], "Contoso", "synthetic-demo")
        _get_or_create_alias(db, employers["fabrikam"], "Fabrikam Security Inc.", "synthetic-demo")
        _get_or_create_alias(db, employers["fabrikam"], "Fabrikam", "synthetic-demo")

        perm_cases = [
            {
                "case_number": "DEMO-2024-0001",
                "employer_id": employers["northwind"].id,
                "fiscal_year": 2024,
                "case_status": "CERTIFIED",
                "filing_date": date(2024, 3, 14),
                "decision_date": date(2024, 8, 9),
                "job_title": "Senior Software Engineer",
                "occupation_id": occupations["software"].id,
                "original_soc_code": occupations["software"].soc_code,
                "original_soc_title": occupations["software"].soc_title,
                "worksite_city": "Seattle",
                "worksite_state": "WA",
                "offered_wage_from": 145000,
                "offered_wage_to": 162000,
                "wage_unit": "Year",
                "source_file": "synthetic_demo_fy2024.csv",
                "source_url": "https://example.com/dol/synthetic-demo-fy2024",
                "source_updated_at": datetime.utcnow() - timedelta(days=60),
            },
            {
                "case_number": "DEMO-2025-0002",
                "employer_id": employers["northwind"].id,
                "fiscal_year": 2025,
                "case_status": "CERTIFIED",
                "filing_date": date(2025, 1, 18),
                "decision_date": date(2025, 6, 12),
                "job_title": "Platform Engineer",
                "occupation_id": occupations["software"].id,
                "original_soc_code": occupations["software"].soc_code,
                "original_soc_title": occupations["software"].soc_title,
                "worksite_city": "Seattle",
                "worksite_state": "WA",
                "offered_wage_from": 152000,
                "offered_wage_to": 168000,
                "wage_unit": "Year",
                "source_file": "synthetic_demo_fy2025.csv",
                "source_url": "https://example.com/dol/synthetic-demo-fy2025",
                "source_updated_at": datetime.utcnow() - timedelta(days=25),
            },
            {
                "case_number": "DEMO-2026-0003",
                "employer_id": employers["contoso"].id,
                "fiscal_year": 2026,
                "case_status": "DENIED",
                "filing_date": date(2026, 2, 10),
                "decision_date": date(2026, 5, 21),
                "job_title": "Data Engineer",
                "occupation_id": occupations["data"].id,
                "original_soc_code": occupations["data"].soc_code,
                "original_soc_title": occupations["data"].soc_title,
                "worksite_city": "Austin",
                "worksite_state": "TX",
                "offered_wage_from": 128000,
                "offered_wage_to": 142000,
                "wage_unit": "Year",
                "source_file": "synthetic_demo_fy2026_ytd.csv",
                "source_url": "https://example.com/dol/synthetic-demo-fy2026",
                "source_updated_at": datetime.utcnow() - timedelta(days=10),
            },
            {
                "case_number": "DEMO-2025-0004",
                "employer_id": employers["contoso"].id,
                "fiscal_year": 2025,
                "case_status": "CERTIFIED-EXPIRED",
                "filing_date": date(2025, 4, 8),
                "decision_date": date(2025, 7, 4),
                "job_title": "Data Scientist",
                "occupation_id": occupations["data"].id,
                "original_soc_code": occupations["data"].soc_code,
                "original_soc_title": occupations["data"].soc_title,
                "worksite_city": "Dallas",
                "worksite_state": "TX",
                "offered_wage_from": 134000,
                "offered_wage_to": 151000,
                "wage_unit": "Year",
                "source_file": "synthetic_demo_fy2025.csv",
                "source_url": "https://example.com/dol/synthetic-demo-fy2025",
                "source_updated_at": datetime.utcnow() - timedelta(days=25),
            },
            {
                "case_number": "DEMO-2023-0005",
                "employer_id": employers["fabrikam"].id,
                "fiscal_year": 2023,
                "case_status": "WITHDRAWN",
                "filing_date": date(2023, 2, 3),
                "decision_date": date(2023, 5, 19),
                "job_title": "Security Engineer",
                "occupation_id": occupations["security"].id,
                "original_soc_code": occupations["security"].soc_code,
                "original_soc_title": occupations["security"].soc_title,
                "worksite_city": "San Jose",
                "worksite_state": "CA",
                "offered_wage_from": 149000,
                "offered_wage_to": 165000,
                "wage_unit": "Year",
                "source_file": "synthetic_demo_fy2023.csv",
                "source_url": "https://example.com/dol/synthetic-demo-fy2023",
                "source_updated_at": datetime.utcnow() - timedelta(days=400),
            },
        ]
        for item in perm_cases:
            _get_or_create_perm_case(db, **item)

        for item in [
            {
                "employer_id": employers["northwind"].id,
                "fiscal_year": 2025,
                "initial_approvals": 12,
                "initial_denials": 1,
                "continuing_approvals": 4,
                "continuing_denials": 0,
                "source": "synthetic-demo",
                "source_updated_at": datetime.utcnow() - timedelta(days=20),
            },
            {
                "employer_id": employers["contoso"].id,
                "fiscal_year": 2025,
                "initial_approvals": 5,
                "initial_denials": 2,
                "continuing_approvals": 2,
                "continuing_denials": 1,
                "source": "synthetic-demo",
                "source_updated_at": datetime.utcnow() - timedelta(days=20),
            },
        ]:
            _get_or_create_h1b_stat(db, **item)

        current_jobs_seed = [
        {
            "external_job_id": "job-001",
            "employer_id": employers["northwind"].id,
            "source": "synthetic-demo-company-careers",
            "source_url": "https://example.com/northwind/jobs/1?demo=1",
            "title": "Staff Platform Engineer",
            "description": "Visa sponsorship available. We sponsor qualified candidates and support permanent residency sponsorship.",
            "city": "Seattle",
            "state": "WA",
            "remote_type": "Hybrid",
            "employment_type": "Full-time",
            "posted_date": date.today() - timedelta(days=7),
            "occupation_id": occupations["software"].id,
        },
        {
            "external_job_id": "job-002",
            "employer_id": employers["contoso"].id,
            "source": "synthetic-demo-company-careers",
            "source_url": "https://example.com/contoso/jobs/2?demo=1",
            "title": "Senior Data Engineer",
            "description": "We have sponsored H-1B and permanent-residency cases in the past. However, this position does not provide sponsorship now or in the future.",
            "city": "Austin",
            "state": "TX",
            "remote_type": "Remote",
            "employment_type": "Full-time",
            "posted_date": date.today() - timedelta(days=14),
            "occupation_id": occupations["data"].id,
        },
        {
            "external_job_id": "job-003",
            "employer_id": employers["fabrikam"].id,
            "source": "synthetic-demo-company-careers",
            "source_url": "https://example.com/fabrikam/jobs/3?demo=1",
            "title": "Security Analyst",
            "description": "Join our cloud security team. Sponsorship policy is not stated in this posting.",
            "city": "San Jose",
            "state": "CA",
            "remote_type": "On-site",
            "employment_type": "Full-time",
            "posted_date": date.today() - timedelta(days=21),
            "occupation_id": occupations["security"].id,
        },
    ]
        for job_seed in current_jobs_seed:
            classification, score, reasons = classifier.classify_sponsorship(job_seed["description"])
            _get_or_create_current_job(
                db,
                **job_seed,
                retrieved_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30),
                sponsorship_classification=classification,
                sponsorship_score=score,
                sponsorship_reasons="||".join(reasons),
                is_active=True,
            )

        for item in [
            {
                "source_name": "OFLC PERM",
                "source_url": "https://example.com/dol/synthetic-demo-fy2026",
                "fiscal_year": 2026,
                "reporting_period": "Year to date",
                "file_name": "synthetic_demo_fy2026_ytd.csv",
                "file_hash": "synthetic-demo-2026",
                "status": "completed",
                "records_processed": 1,
                "records_inserted": 1,
                "records_updated": 0,
                "records_rejected": 0,
                "started_at": datetime.utcnow() - timedelta(days=10, minutes=5),
                "completed_at": datetime.utcnow() - timedelta(days=10),
                "error_message": None,
            },
            {
                "source_name": "OFLC PERM",
                "source_url": "https://example.com/dol/synthetic-demo-fy2025",
                "fiscal_year": 2025,
                "reporting_period": "Complete",
                "file_name": "synthetic_demo_fy2025.csv",
                "file_hash": "synthetic-demo-2025",
                "status": "completed",
                "records_processed": 2,
                "records_inserted": 2,
                "records_updated": 0,
                "records_rejected": 0,
                "started_at": datetime.utcnow() - timedelta(days=25, minutes=5),
                "completed_at": datetime.utcnow() - timedelta(days=25),
                "error_message": None,
            },
        ]:
            _get_or_create_import(db, **item)
        db.commit()
        logger.info("Synthetic demo seed ensured for employers, occupations, PERM cases, jobs, and imports.")
    except Exception:
        db.rollback()
        logger.exception("Synthetic demo seed failed and was rolled back.")
        raise
