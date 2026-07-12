from app.services.database_summary_service import get_database_summary


def test_seed_creates_expected_demo_dataset(seeded_session):
    summary = get_database_summary(seeded_session)
    assert summary["availableFiscalYears"] == [2026, 2025, 2024, 2023]
    assert summary["availableStates"] == ["CA", "TX", "WA"]
