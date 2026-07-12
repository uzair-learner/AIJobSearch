from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import CurrentJob, Employer, H1BEmployerStatistics, Occupation, PermCase
from app.schemas.search import SearchResultItem, SponsorSearchRequest, SponsorSearchResponse
from app.services.sponsorship_score_service import SponsorshipScoreService
from app.utils.salary_normalizer import average_salary
from app.utils.text_normalizer import normalize_title


SORT_FIELDS = {
    "recent_filings": "recent_filing_date",
    "highest_certified": "number_certified",
    "highest_certification_rate": "certification_rate",
    "most_current_jobs": "current_job_count",
    "most_sponsored_current_jobs": "current_sponsored_job_count",
    "highest_sponsorship_score": "sponsorship_score",
    "highest_average_salary": "offered_wage",
    "employer_name": "employer_name",
    "newest_filing_date": "recent_filing_date",
}


class SponsorSearchService:
    def __init__(self) -> None:
        self.score_service = SponsorshipScoreService()

    def search(self, db: Session, request: SponsorSearchRequest) -> SponsorSearchResponse:
        query = (
            select(Employer)
            .options(
                selectinload(Employer.perm_cases).selectinload(PermCase.occupation),
                selectinload(Employer.current_jobs),
                selectinload(Employer.h1b_stats),
                selectinload(Employer.aliases),
            )
            .join(PermCase)
            .distinct()
        )

        if request.searchText:
            term = request.searchText.lower()
            query = query.join(Employer.perm_cases).outerjoin(PermCase.occupation).where(
                Employer.display_name.ilike(f"%{term}%")
                | Employer.normalized_name.ilike(f"%{term.upper()}%")
                | PermCase.job_title.ilike(f"%{term}%")
                | PermCase.worksite_city.ilike(f"%{term}%")
                | PermCase.worksite_state.ilike(f"%{term}%")
                | Occupation.soc_title.ilike(f"%{term}%")
                | Occupation.soc_code.ilike(f"%{term}%")
            )
        employers = db.scalars(query).unique().all()

        results: list[SearchResultItem] = []
        for employer in employers:
            perm_cases = list(employer.perm_cases)
            if request.fiscalYears:
                perm_cases = [case for case in perm_cases if case.fiscal_year in request.fiscalYears]
            if request.professionIds:
                perm_cases = [case for case in perm_cases if case.occupation_id in request.professionIds]
            if request.states:
                perm_cases = [case for case in perm_cases if case.worksite_state in request.states]
            if request.caseStatuses:
                perm_cases = [case for case in perm_cases if case.case_status in request.caseStatuses]
            if request.dateRecency == "last_3_fiscal_years":
                max_year = max((case.fiscal_year for case in employer.perm_cases), default=None)
                if max_year is not None:
                    perm_cases = [case for case in perm_cases if case.fiscal_year >= max_year - 2]
            if not perm_cases:
                continue

            status_counts = Counter(case.case_status for case in perm_cases)
            certified_count = status_counts.get("CERTIFIED", 0) + status_counts.get("CERTIFIED-EXPIRED", 0)
            if len(perm_cases) < request.minimumFilings:
                continue

            current_jobs = [job for job in employer.current_jobs if job.is_active]
            if request.states:
                current_jobs = [job for job in current_jobs if job.state in request.states]
            sponsored_jobs = [
                job for job in current_jobs if job.sponsorship_classification in {"explicit_sponsorship", "may_consider"}
            ]
            denied_jobs = [job for job in current_jobs if job.sponsorship_classification == "sponsorship_unavailable"]

            if request.evidenceType == "historical_with_current_jobs" and not current_jobs:
                continue
            if request.evidenceType == "current_job_explicit" and not any(
                job.sponsorship_classification == "explicit_sponsorship" for job in current_jobs
            ):
                continue
            if request.evidenceType == "h1b_perm" and not employer.h1b_stats:
                continue

            recent_years = sorted({case.fiscal_year for case in perm_cases}, reverse=True)
            latest_year = recent_years[0]
            years_since_recent = datetime.utcnow().year - latest_year if latest_year else None
            occupation_counts = Counter(
                case.occupation.soc_title for case in perm_cases if case.occupation and case.occupation.soc_title
            )
            job_title_counts = Counter(case.job_title for case in perm_cases if case.job_title)
            city_counts = Counter(case.worksite_city for case in perm_cases if case.worksite_city)
            state_counts = Counter(case.worksite_state for case in perm_cases if case.worksite_state)
            average_wages = [
                average_salary(case.offered_wage_from, case.offered_wage_to)
                for case in perm_cases
                if average_salary(case.offered_wage_from, case.offered_wage_to) is not None
            ]
            most_recent_case = max(
                perm_cases,
                key=lambda case: (case.fiscal_year, case.filing_date.isoformat() if case.filing_date else ""),
            )
            selected_occ_certified = len(
                [
                    case
                    for case in perm_cases
                    if case.case_status.startswith("CERTIFIED")
                    and (
                        not request.professionIds
                        or case.occupation_id in request.professionIds
                    )
                ]
            )
            score = self.score_service.calculate(
                recent_certified_filings=certified_count,
                certified_in_selected_occupation=selected_occ_certified,
                recent_year_count=len([year for year in recent_years if year >= latest_year - 2]),
                has_h1b_history=bool(employer.h1b_stats),
                explicit_job_support_count=len(
                    [job for job in current_jobs if job.sponsorship_classification == "explicit_sponsorship"]
                ),
                explicit_job_denial_count=len(denied_jobs),
                years_since_recent_activity=years_since_recent,
            )
            results.append(
                SearchResultItem(
                    employerId=employer.id,
                    employerName=employer.display_name,
                    normalizedEmployerName=employer.normalized_name,
                    fiscalYear=latest_year,
                    numberOfPermFilings=len(perm_cases),
                    numberCertified=certified_count,
                    numberDenied=status_counts.get("DENIED", 0),
                    numberWithdrawn=status_counts.get("WITHDRAWN", 0),
                    certificationRate=round((certified_count / len(perm_cases)) * 100, 1),
                    primaryOccupation=occupation_counts.most_common(1)[0][0] if occupation_counts else None,
                    socCode=most_recent_case.occupation.soc_code if most_recent_case.occupation else None,
                    topJobTitle=job_title_counts.most_common(1)[0][0] if job_title_counts else None,
                    worksiteCity=city_counts.most_common(1)[0][0] if city_counts else None,
                    worksiteState=state_counts.most_common(1)[0][0] if state_counts else None,
                    offeredWage=round(sum(average_wages) / len(average_wages), 2) if average_wages else None,
                    wageUnit=most_recent_case.wage_unit,
                    filingDate=most_recent_case.filing_date.isoformat() if most_recent_case.filing_date else None,
                    decisionDate=most_recent_case.decision_date.isoformat() if most_recent_case.decision_date else None,
                    caseStatus=most_recent_case.case_status,
                    dataSource="U.S. Department of Labor OFLC PERM disclosure data",
                    dataUpdatedDate=most_recent_case.source_updated_at.isoformat() if most_recent_case.source_updated_at else None,
                    currentJobCount=len(current_jobs),
                    currentSponsoredJobCount=len(sponsored_jobs),
                    h1bSponsorshipHistory=bool(employer.h1b_stats),
                    sponsorshipConfidenceLevel=score.label,
                    sponsorshipScore=score.score,
                    sponsorshipReasons=score.reasons,
                    dataLimitations=score.limitations,
                )
            )

        reverse = request.sortDirection == "desc"
        sort_field = SORT_FIELDS.get(request.sortBy, "fiscalYear")
        results.sort(key=lambda item: getattr(item, self._field_map(sort_field)), reverse=reverse)

        total = len(results)
        start = (request.page - 1) * request.pageSize
        page_results = results[start : start + request.pageSize]
        return SponsorSearchResponse(
            page=request.page,
            pageSize=request.pageSize,
            totalRecords=total,
            totalPages=max(1, (total + request.pageSize - 1) // request.pageSize),
            results=page_results,
            generatedAt=datetime.utcnow(),
        )

    def _field_map(self, sort_field: str) -> str:
        mapping = {
            "recent_filing_date": "filingDate",
            "number_certified": "numberCertified",
            "certification_rate": "certificationRate",
            "current_job_count": "currentJobCount",
            "current_sponsored_job_count": "currentSponsoredJobCount",
            "sponsorship_score": "sponsorshipScore",
            "offered_wage": "offeredWage",
            "employer_name": "employerName",
            "fiscalYear": "fiscalYear",
        }
        return mapping.get(sort_field, "fiscalYear")

    def employer_statistics(self, db: Session, employer_id: int) -> dict:
        employer = db.get(Employer, employer_id)
        if not employer:
            return {}
        filings_by_year = defaultdict(int)
        outcomes_by_year: dict[int, Counter] = defaultdict(Counter)
        occupation_counts = Counter()
        title_counts = Counter()
        state_counts = Counter()
        salaries_by_year: dict[int, list[float]] = defaultdict(list)
        job_locations = Counter()
        for case in employer.perm_cases:
            filings_by_year[case.fiscal_year] += 1
            outcomes_by_year[case.fiscal_year][case.case_status] += 1
            if case.occupation:
                occupation_counts[case.occupation.soc_title] += 1
            if case.job_title:
                title_counts[normalize_title(case.job_title)] += 1
            if case.worksite_state:
                state_counts[case.worksite_state] += 1
            avg = average_salary(case.offered_wage_from, case.offered_wage_to)
            if avg is not None:
                salaries_by_year[case.fiscal_year].append(avg)
        for job in employer.current_jobs:
            job_locations[f"{job.city or 'Remote'}, {job.state or 'N/A'}"] += 1

        return {
            "filingsByFiscalYear": [
                {"fiscalYear": year, "count": count} for year, count in sorted(filings_by_year.items(), reverse=True)
            ],
            "outcomesByYear": [
                {"fiscalYear": year, **dict(counter)} for year, counter in sorted(outcomes_by_year.items(), reverse=True)
            ],
            "topOccupations": [{"label": label, "count": count} for label, count in occupation_counts.most_common(5)],
            "topJobTitles": [{"label": label, "count": count} for label, count in title_counts.most_common(5)],
            "topStates": [{"label": label, "count": count} for label, count in state_counts.most_common(5)],
            "averageSalaryByYear": [
                {"fiscalYear": year, "averageSalary": round(sum(values) / len(values), 2)}
                for year, values in sorted(salaries_by_year.items(), reverse=True)
            ],
            "currentJobsByLocation": [{"label": label, "count": count} for label, count in job_locations.most_common(5)],
        }
