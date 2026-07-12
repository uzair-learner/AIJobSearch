from sqlalchemy import select

from app.models import Occupation
from app.services.occupation_service import OccupationService


def test_it_occupation_metadata_is_seeded(seeded_session):
    occupations = OccupationService().list_it_professions(seeded_session)
    assert len(occupations) >= 3
    assert any(item.socCode == "15-1252" for item in occupations)


def test_available_occupation_codes_exist(seeded_session):
    codes = seeded_session.scalars(select(Occupation.soc_code)).all()
    assert {"15-1252", "15-2051", "15-1212"}.issubset(set(codes))
