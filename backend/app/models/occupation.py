from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Occupation(Base):
    __tablename__ = "occupations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    soc_code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    soc_title: Mapped[str] = mapped_column(String(255), nullable=False)
    profession_category: Mapped[str | None] = mapped_column(String(100))
    normalized_title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    is_it_profession: Mapped[bool] = mapped_column(Boolean, default=True)
    source_year: Mapped[int | None] = mapped_column(Integer)

    perm_cases: Mapped[list["PermCase"]] = relationship(back_populates="occupation")
    current_jobs: Mapped[list["CurrentJob"]] = relationship(back_populates="occupation")
