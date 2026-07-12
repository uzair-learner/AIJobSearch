from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employer(Base):
    __tablename__ = "employers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(50))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(100), default="USA")
    website: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    aliases: Mapped[list["EmployerAlias"]] = relationship(back_populates="employer", cascade="all, delete-orphan")
    perm_cases: Mapped[list["PermCase"]] = relationship(back_populates="employer", cascade="all, delete-orphan")
    h1b_stats: Mapped[list["H1BEmployerStatistics"]] = relationship(back_populates="employer", cascade="all, delete-orphan")
    current_jobs: Mapped[list["CurrentJob"]] = relationship(back_populates="employer", cascade="all, delete-orphan")


class EmployerAlias(Base):
    __tablename__ = "employer_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("employers.id"), index=True, nullable=False)
    alias_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="demo")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    manually_verified: Mapped[bool] = mapped_column(default=False)

    employer: Mapped["Employer"] = relationship(back_populates="aliases")
