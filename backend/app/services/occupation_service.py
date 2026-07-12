from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Occupation
from app.schemas.occupation import OccupationMetadataItem


class OccupationService:
    def list_it_professions(self, db: Session) -> list[OccupationMetadataItem]:
        occupations = db.scalars(
            select(Occupation).where(Occupation.is_it_profession.is_(True)).order_by(Occupation.soc_title.asc())
        ).all()
        return [
            OccupationMetadataItem(
                id=occupation.id,
                socCode=occupation.soc_code,
                socTitle=occupation.soc_title,
                professionCategory=occupation.profession_category,
            )
            for occupation in occupations
        ]
