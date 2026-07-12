from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PermCase(Base):
    __tablename__ = "perm_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    employer_id: Mapped[int] = mapped_column(ForeignKey("employers.id"), index=True, nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    case_status: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    filing_date: Mapped[date | None] = mapped_column(Date)
    decision_date: Mapped[date | None] = mapped_column(Date)
    job_title: Mapped[str | None] = mapped_column(String(255))
    occupation_id: Mapped[int | None] = mapped_column(ForeignKey("occupations.id"))
    original_soc_code: Mapped[str | None] = mapped_column(String(20))
    original_soc_title: Mapped[str | None] = mapped_column(String(255))
    worksite_city: Mapped[str | None] = mapped_column(String(120))
    worksite_state: Mapped[str | None] = mapped_column(String(50), index=True)
    worksite_postal_code: Mapped[str | None] = mapped_column(String(20))
    offered_wage_from: Mapped[float | None] = mapped_column(Float)
    offered_wage_to: Mapped[float | None] = mapped_column(Float)
    wage_unit: Mapped[str | None] = mapped_column(String(50))
    minimum_education: Mapped[str | None] = mapped_column(String(120))
    major_field: Mapped[str | None] = mapped_column(String(120))
    experience_required: Mapped[str | None] = mapped_column(String(120))
    foreign_worker_education: Mapped[str | None] = mapped_column(String(120))
    source_file: Mapped[str | None] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(500))
    imported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    employer: Mapped["Employer"] = relationship(back_populates="perm_cases")
    occupation: Mapped["Occupation"] = relationship(back_populates="perm_cases")
