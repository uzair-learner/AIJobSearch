from app.services.current_job_service import CurrentJobService


def test_negative_language_overrides_positive_keywords() -> None:
    service = CurrentJobService()
    classification, score, _ = service.classify_sponsorship(
        "We have sponsored H-1B and permanent-residency cases in the past. However, this position does not provide sponsorship now or in the future."
    )
    assert classification == "sponsorship_unavailable"
    assert score == 0
