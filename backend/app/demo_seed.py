from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CurrentJob, DataImport, Employer, EmployerAlias, H1BEmployerStatistics, Occupation, PermCase
from app.services.current_job_service import CurrentJobService
from app.utils.text_normalizer import normalize_employer_name, normalize_title


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(Employer.id).limit(1)):
        return

    occupations = [
        Occupation(
            soc_code="15-1252",
            soc_title="Software Developers",
            profession_category="Software development",
            normalized_title=normalize_title("Software Developers"),
            is_it_profession=True,
            source_year=2026,
        ),
        Occupation(
            soc_code="15-2051",
            soc_title="Data Scientists",
            profession_category="Data and databases",
            normalized_title=normalize_title("Data Scientists"),
            is_it_profession=True,
            source_year=2026,
        ),
        Occupation(
            soc_code="15-1212",
            soc_title="Information Security Analysts",
            profession_category="Cybersecurity",
            normalized_title=normalize_title("Information Security Analysts"),
            is_it_profession=True,
            source_year=2026,
        ),
    ]
    db.add_all(occupations)
    db.flush()

    employers = [
        Employer(
            original_name="Northwind Cloud Corporation",
            normalized_name=normalize_employer_name("Northwind Cloud Corporation"),
            display_name="Northwind Cloud",
            city="Seattle",
            state="WA",
            website="https://example.com/northwind",
        ),
        Employer(
            original_name="Contoso Analytics LLC",
            normalized_name=normalize_employer_name("Contoso Analytics LLC"),
            display_name="Contoso Analytics",
            city="Austin",
            state="TX",
            website="https://example.com/contoso",
        ),
        Employer(
            original_name="Fabrikam Security Inc.",
            normalized_name=normalize_employer_name("Fabrikam Security Inc."),
            display_name="Fabrikam Security",
            city="San Jose",
            state="CA",
            website="https://example.com/fabrikam",
        ),
    ]
    db.add_all(employers)
    db.flush()

    for employer in employers:
        db.add(
            EmployerAlias(
                employer_id=employer.id,
                alias_name=employer.original_name,
                normalized_alias=employer.normalized_name,
                source="demo",
                confidence=1.0,
                manually_verified=True,
            )
        )

    perm_cases = [
        PermCase(
            case_number="DEMO-2024-0001",
            employer_id=employers[0].id,
            fiscal_year=2024,
            case_status="CERTIFIED",
            filing_date=date(2024, 3, 14),
            decision_date=date(2024, 8, 9),
            job_title="Senior Software Engineer",
            occupation_id=occupations[0].id,
            original_soc_code=occupations[0].soc_code,
            original_soc_title=occupations[0].soc_title,
            worksite_city="Seattle",
            worksite_state="WA",
            offered_wage_from=145000,
            offered_wage_to=162000,
            wage_unit="Year",
            source_file="demo_fy2024.csv",
            source_url="https://www.dol.gov",
            source_updated_at=datetime.utcnow() - timedelta(days=60),
        ),
        PermCase(
            case_number="DEMO-2025-0002",
            employer_id=employers[0].id,
            fiscal_year=2025,
            case_status="CERTIFIED",
            filing_date=date(2025, 1, 18),
            decision_date=date(2025, 6, 12),
            job_title="Platform Engineer",
            occupation_id=occupations[0].id,
            original_soc_code=occupations[0].soc_code,
            original_soc_title=occupations[0].soc_title,
            worksite_city="Seattle",
            worksite_state="WA",
            offered_wage_from=152000,
            offered_wage_to=168000,
            wage_unit="Year",
            source_file="demo_fy2025.csv",
            source_url="https://www.dol.gov",
            source_updated_at=datetime.utcnow() - timedelta(days=25),
        ),
        PermCase(
            case_number="DEMO-2026-0003",
            employer_id=employers[1].id,
            fiscal_year=2026,
            case_status="DENIED",
            filing_date=date(2026, 2, 10),
            decision_date=date(2026, 5, 21),
            job_title="Data Engineer",
            occupation_id=occupations[1].id,
            original_soc_code=occupations[1].soc_code,
            original_soc_title=occupations[1].soc_title,
            worksite_city="Austin",
            worksite_state="TX",
            offered_wage_from=128000,
            offered_wage_to=142000,
            wage_unit="Year",
            source_file="demo_fy2026_ytd.csv",
            source_url="https://www.dol.gov",
            source_updated_at=datetime.utcnow() - timedelta(days=10),
        ),
        PermCase(
            case_number="DEMO-2025-0004",
            employer_id=employers[1].id,
            fiscal_year=2025,
            case_status="CERTIFIED-EXPIRED",
            filing_date=date(2025, 4, 8),
            decision_date=date(2025, 7, 4),
            job_title="Data Scientist",
            occupation_id=occupations[1].id,
            original_soc_code=occupations[1].soc_code,
            original_soc_title=occupations[1].soc_title,
            worksite_city="Dallas",
            worksite_state="TX",
            offered_wage_from=134000,
            offered_wage_to=151000,
            wage_unit="Year",
            source_file="demo_fy2025.csv",
            source_url="https://www.dol.gov",
            source_updated_at=datetime.utcnow() - timedelta(days=25),
        ),
        PermCase(
            case_number="DEMO-2023-0005",
            employer_id=employers[2].id,
            fiscal_year=2023,
            case_status="WITHDRAWN",
            filing_date=date(2023, 2, 3),
            decision_date=date(2023, 5, 19),
            job_title="Security Engineer",
            occupation_id=occupations[2].id,
            original_soc_code=occupations[2].soc_code,
            original_soc_title=occupations[2].soc_title,
            worksite_city="San Jose",
            worksite_state="CA",
            offered_wage_from=149000,
            offered_wage_to=165000,
            wage_unit="Year",
            source_file="demo_fy2023.csv",
            source_url="https://www.dol.gov",
            source_updated_at=datetime.utcnow() - timedelta(days=400),
        ),
    ]
    db.add_all(perm_cases)

    h1b_stats = [
        H1BEmployerStatistics(
            employer_id=employers[0].id,
            fiscal_year=2025,
            initial_approvals=12,
            initial_denials=1,
            continuing_approvals=4,
            continuing_denials=0,
            source="demo",
            source_updated_at=datetime.utcnow() - timedelta(days=20),
        ),
        H1BEmployerStatistics(
            employer_id=employers[1].id,
            fiscal_year=2025,
            initial_approvals=5,
            initial_denials=2,
            continuing_approvals=2,
            continuing_denials=1,
            source="demo",
            source_updated_at=datetime.utcnow() - timedelta(days=20),
        ),
    ]
    db.add_all(h1b_stats)

    classifier = CurrentJobService()
    current_jobs_seed = [
        {
            "external_job_id": "job-001",
            "employer_id": employers[0].id,
            "source": "demo-company-careers",
            "source_url": "https://example.com/northwind/jobs/1",
            "title": "Staff Platform Engineer",
            "description": "Visa sponsorship available. We sponsor qualified candidates and support permanent residency sponsorship.",
            "city": "Seattle",
            "state": "WA",
            "remote_type": "Hybrid",
            "employment_type": "Full-time",
            "posted_date": date.today() - timedelta(days=7),
            "occupation_id": occupations[0].id,
        },
        {
            "external_job_id": "job-002",
            "employer_id": employers[1].id,
            "source": "demo-company-careers",
            "source_url": "https://example.com/contoso/jobs/2",
            "title": "Senior Data Engineer",
            "description": "We have sponsored H-1B and permanent-residency cases in the past. However, this position does not provide sponsorship now or in the future.",
            "city": "Austin",
            "state": "TX",
            "remote_type": "Remote",
            "employment_type": "Full-time",
            "posted_date": date.today() - timedelta(days=14),
            "occupation_id": occupations[1].id,
        },
        {
            "external_job_id": "job-003",
            "employer_id": employers[2].id,
            "source": "demo-company-careers",
            "source_url": "https://example.com/fabrikam/jobs/3",
            "title": "Security Analyst",
            "description": "Join our cloud security team. Sponsorship policy is not stated in this posting.",
            "city": "San Jose",
            "state": "CA",
            "remote_type": "On-site",
            "employment_type": "Full-time",
            "posted_date": date.today() - timedelta(days=21),
            "occupation_id": occupations[2].id,
        },
    ]
    for job_seed in current_jobs_seed:
        classification, score, reasons = classifier.classify_sponsorship(job_seed["description"])
        db.add(
            CurrentJob(
                **job_seed,
                retrieved_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30),
                sponsorship_classification=classification,
                sponsorship_score=score,
                sponsorship_reasons="||".join(reasons),
                is_active=True,
            )
        )

    imports = [
        DataImport(
            source_name="OFLC PERM",
            source_url="https://www.dol.gov",
            fiscal_year=2026,
            reporting_period="Year to date",
            file_name="demo_fy2026_ytd.csv",
            file_hash="demo-2026",
            status="completed",
            records_processed=1,
            records_inserted=1,
            records_updated=0,
            records_rejected=0,
            started_at=datetime.utcnow() - timedelta(days=10, minutes=5),
            completed_at=datetime.utcnow() - timedelta(days=10),
            error_message=None,
        ),
        DataImport(
            source_name="OFLC PERM",
            source_url="https://www.dol.gov",
            fiscal_year=2025,
            reporting_period="Complete",
            file_name="demo_fy2025.csv",
            file_hash="demo-2025",
            status="completed",
            records_processed=2,
            records_inserted=2,
            records_updated=0,
            records_rejected=0,
            started_at=datetime.utcnow() - timedelta(days=25, minutes=5),
            completed_at=datetime.utcnow() - timedelta(days=25),
            error_message=None,
        ),
    ]
    db.add_all(imports)
    db.commit()
