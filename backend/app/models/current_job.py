from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CurrentJob(Base):
    __tablename__ = "current_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_job_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    employer_id: Mapped[int] = mapped_column(ForeignKey("employers.id"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(50), index=True)
    remote_type: Mapped[str | None] = mapped_column(String(50))
    employment_type: Mapped[str | None] = mapped_column(String(50))
    posted_date: Mapped[date | None] = mapped_column(Date)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    occupation_id: Mapped[int | None] = mapped_column(ForeignKey("occupations.id"))
    sponsorship_classification: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    sponsorship_score: Mapped[int] = mapped_column(Integer, default=0)
    sponsorship_reasons: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    employer: Mapped["Employer"] = relationship(back_populates="current_jobs")
    occupation: Mapped["Occupation"] = relationship(back_populates="current_jobs")
