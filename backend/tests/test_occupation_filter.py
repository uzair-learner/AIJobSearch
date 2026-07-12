from app.services.occupation_service import OccupationService


def test_placeholder() -> None:
    service = OccupationService()
    assert service is not None
