from sqlalchemy import delete, select

from app.demo_seed import seed_demo_data
from app.models import Employer, Occupation, PermCase
from app.services.database_summary_service import get_database_summary
from app.services.sponsor_search_service import SponsorSearchService


def _search(service: SponsorSearchService, session, **overrides):
    payload = {
        "searchText": "",
        "fiscalYears": [],
        "professionIds": [],
        "states": [],
        "caseStatuses": [],
        "minimumFilings": 1,
        "evidenceType": "all",
        "dateRecency": "all",
        "page": 1,
        "pageSize": 25,
        "sortBy": "recent_filings",
        "sortDirection": "desc",
    }
    payload.update(overrides)
    from app.schemas.search import SponsorSearchRequest

    return service.search(session, SponsorSearchRequest(**payload))


def test_fresh_database_seed_counts(seeded_session):
    summary = get_database_summary(seeded_session)
    assert summary["employers"] == 3
    assert summary["occupations"] >= 3
    assert summary["permCases"] >= 5


def test_seed_is_idempotent(seeded_session):
    first = get_database_summary(seeded_session)
    seed_demo_data(seeded_session)
    second = get_database_summary(seeded_session)
    assert first["employers"] == second["employers"]
    assert first["occupations"] == second["occupations"]
    assert first["permCases"] == second["permCases"]


def test_partially_seeded_database_is_repaired(session):
    session.add(
        Employer(
            original_name="Northwind Cloud Corporation",
            normalized_name="NORTHWIND CLOUD CORP",
            display_name="Northwind Cloud",
            city="Seattle",
            state="WA",
            website="https://example.com",
        )
    )
    session.commit()
    seed_demo_data(session)
    summary = get_database_summary(session)
    assert summary["employers"] == 3
    assert summary["occupations"] >= 3
    assert summary["permCases"] >= 5


def test_search_software_returns_northwind(seeded_session):
    response = _search(SponsorSearchService(), seeded_session, searchText="software")
    results = response.results
    assert results[0].employerName == "Northwind Cloud"
    assert response.totalMatchingEmployers == 1
    assert response.totalMatchingPermCases == 2


def test_search_software_returns_two_matching_filings(seeded_session):
    response = _search(SponsorSearchService(), seeded_session, searchText="software", resultView="filings")
    assert response.resultView == "filings"
    assert response.totalMatchingEmployers == 1
    assert response.totalMatchingPermCases == 2
    assert len(response.results) == 2
    assert {item.caseNumber for item in response.results} == {"DEMO-2024-0001", "DEMO-2025-0002"}


def test_search_software_developers_returns_northwind(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Software Developers").results
    assert [item.employerName for item in results] == ["Northwind Cloud"]


def test_search_data_returns_contoso(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="data").results
    assert [item.employerName for item in results] == ["Contoso Analytics"]


def test_search_data_scientists_returns_contoso(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Data Scientists").results
    assert [item.employerName for item in results] == ["Contoso Analytics"]


def test_search_security_returns_fabrikam(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="security").results
    assert [item.employerName for item in results] == ["Fabrikam Security"]


def test_search_information_security_analysts_returns_fabrikam(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Information Security Analysts").results
    assert [item.employerName for item in results] == ["Fabrikam Security"]


def test_employer_alias_search_works(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Contoso").results
    assert [item.employerName for item in results] == ["Contoso Analytics"]


def test_unknown_search_returns_zero_results(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="unknown-phrase").results
    assert results == []


def test_all_years_applies_no_filter(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Northwind").results
    assert results[0].numberOfPermFilings == 2


def test_selected_year_filters_correctly(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Northwind", fiscalYears=[2025]).results
    assert results[0].numberOfPermFilings == 1


def test_selected_state_filters_correctly(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="WA", states=["WA"]).results
    assert [item.employerName for item in results] == ["Northwind Cloud"]


def test_selected_occupation_filters_correctly(seeded_session):
    profession_id = seeded_session.scalar(select(Occupation.id).where(Occupation.soc_code == "15-2051"))
    results = _search(SponsorSearchService(), seeded_session, searchText="Contoso", professionIds=[profession_id]).results
    assert [item.employerName for item in results] == ["Contoso Analytics"]


def test_minimum_filing_count_works(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Northwind", minimumFilings=2).results
    assert [item.employerName for item in results] == ["Northwind Cloud"]
    assert _search(SponsorSearchService(), seeded_session, searchText="Fabrikam", minimumFilings=2).results == []


def test_case_level_matching_aggregates_only_matching_cases(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="platform engineer").results
    assert results[0].employerName == "Northwind Cloud"
    assert results[0].numberOfPermFilings == 1


def test_employer_name_matching_aggregates_all_filtered_cases(seeded_session):
    results = _search(SponsorSearchService(), seeded_session, searchText="Northwind").results
    assert results[0].numberOfPermFilings == 2


def test_employer_view_includes_separate_matching_filings(seeded_session):
    response = _search(SponsorSearchService(), seeded_session, searchText="software", resultView="employers")
    assert response.resultView == "employers"
    assert len(response.results) == 1
    employer = response.results[0]
    assert employer.numberOfPermFilings == 2
    assert len(employer.matchingFilings) == 2
    assert employer.matchingFilings[0].caseNumber != employer.matchingFilings[1].caseNumber


def test_database_summary_endpoint_counts_and_safety(client):
    response = client.get("/api/health/database-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["employers"] == 3
    assert data["permCases"] >= 5
    assert "database_url" not in str(data).lower()
    assert "visa_sponsor_jobs.db" not in str(data)


def test_empty_search_request_returns_validation_error(client):
    response = client.post(
        "/api/sponsors/search",
        json={
            "searchText": "",
            "fiscalYears": [],
            "professionIds": [],
            "states": [],
            "caseStatuses": [],
            "minimumFilings": 1,
            "evidenceType": "all",
            "dateRecency": "all",
            "page": 1,
            "pageSize": 25,
            "sortBy": "recent_filings",
            "sortDirection": "desc",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "At least one search condition is required."
