from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import CurrentJob, DataImport, Employer, Occupation, PermCase


def get_database_summary(db: Session) -> dict:
    settings = get_settings()
    fiscal_years = db.scalars(select(distinct(PermCase.fiscal_year)).order_by(PermCase.fiscal_year.desc())).all()
    states = db.scalars(select(distinct(PermCase.worksite_state)).order_by(PermCase.worksite_state.asc())).all()
    occupations = db.execute(
        select(Occupation.soc_code, Occupation.soc_title)
        .where(Occupation.is_it_profession.is_(True))
        .order_by(Occupation.soc_title.asc())
    ).all()
    imports = db.execute(select(DataImport.file_name, DataImport.status)).all()
    official_perm_data_imported = any(
        status == "completed" and "synthetic_demo" not in (file_name or "").lower() for file_name, status in imports
    )
    return {
        "databaseType": "sqlite" if settings.database_url.startswith("sqlite") else "postgresql",
        "demoSeedEnabled": settings.enable_demo_seed,
        "officialPermDataImported": official_perm_data_imported,
        "employers": db.scalar(select(func.count()).select_from(Employer)) or 0,
        "occupations": db.scalar(select(func.count()).select_from(Occupation)) or 0,
        "permCases": db.scalar(select(func.count()).select_from(PermCase)) or 0,
        "currentJobs": db.scalar(select(func.count()).select_from(CurrentJob)) or 0,
        "imports": len(imports),
        "availableFiscalYears": [year for year in fiscal_years if year is not None],
        "availableStates": [state for state in states if state],
        "availableOccupations": [{"socCode": soc_code, "socTitle": soc_title} for soc_code, soc_title in occupations],
    }
