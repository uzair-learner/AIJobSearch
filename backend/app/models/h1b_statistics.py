from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class H1BEmployerStatistics(Base):
    __tablename__ = "h1b_employer_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("employers.id"), index=True, nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    initial_approvals: Mapped[int] = mapped_column(Integer, default=0)
    initial_denials: Mapped[int] = mapped_column(Integer, default=0)
    continuing_approvals: Mapped[int] = mapped_column(Integer, default=0)
    continuing_denials: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(100), default="demo")
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    employer: Mapped["Employer"] = relationship(back_populates="h1b_stats")
