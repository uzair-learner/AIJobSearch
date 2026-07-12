from datetime import datetime
from io import BytesIO

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.importers.mappings import YEAR_MAPPINGS
from app.models import DataImport, Employer, EmployerAlias, Occupation, PermCase
from app.services.current_job_service import CurrentJobService
from app.utils.checksum import file_checksum
from app.utils.text_normalizer import normalize_employer_name, normalize_title


class PermImporter:
    def __init__(self) -> None:
        self.current_job_service = CurrentJobService()

    def import_bytes(
        self,
        db: Session,
        *,
        file_name: str,
        content: bytes,
        fiscal_year: int,
        reporting_period: str,
        source_url: str | None = None,
    ) -> DataImport:
        checksum = file_checksum(content)
        existing = db.scalar(select(DataImport).where(DataImport.file_hash == checksum))
        if existing:
            raise ValueError("This file has already been imported.")

        record = DataImport(
            source_name="OFLC PERM",
            source_url=source_url,
            fiscal_year=fiscal_year,
            reporting_period=reporting_period,
            file_name=file_name,
            file_hash=checksum,
            status="processing",
            started_at=datetime.utcnow(),
        )
        db.add(record)
        db.flush()

        mapping = YEAR_MAPPINGS.get(fiscal_year)
        if not mapping:
            record.status = "failed"
            record.error_message = f"No schema mapping configured for fiscal year {fiscal_year}."
            db.commit()
            return record

        dataframe = self._read_dataframe(file_name, content)
        record.records_processed = len(dataframe)

        required_columns = set(mapping.values())
        missing = required_columns.difference(set(dataframe.columns))
        if missing:
            record.status = "failed"
            record.error_message = f"Missing required columns: {', '.join(sorted(missing))}"
            record.completed_at = datetime.utcnow()
            db.commit()
            return record

        processed = 0
        inserted = 0
        rejected = 0
        for row in dataframe.to_dict(orient="records"):
            processed += 1
            try:
                case_number = str(row[mapping["case_number"]]).strip()
                if not case_number:
                    rejected += 1
                    continue
                existing_case = db.scalar(select(PermCase).where(PermCase.case_number == case_number))
                if existing_case:
                    continue

                employer_name = str(row[mapping["employer_name"]]).strip()
                normalized_employer = normalize_employer_name(employer_name)
                employer = db.scalar(select(Employer).where(Employer.normalized_name == normalized_employer))
                if not employer:
                    employer = Employer(
                        original_name=employer_name,
                        normalized_name=normalized_employer,
                        display_name=employer_name.title(),
                        city=row.get("EMPLOYER_CITY"),
                        state=row.get("EMPLOYER_STATE"),
                        website=None,
                    )
                    db.add(employer)
                    db.flush()
                    db.add(
                        EmployerAlias(
                            employer_id=employer.id,
                            alias_name=employer_name,
                            normalized_alias=normalized_employer,
                            source="perm_import",
                            confidence=1.0,
                            manually_verified=False,
                        )
                    )

                soc_code = str(row.get(mapping["soc_code"], "")).strip()
                soc_title = str(row.get(mapping["soc_title"], "")).strip()
                normalized_title = normalize_title(soc_title or row.get(mapping["job_title"], ""))
                occupation = None
                if soc_code or soc_title:
                    occupation = db.scalar(select(Occupation).where(Occupation.soc_code == soc_code))
                    if not occupation:
                        occupation = Occupation(
                            soc_code=soc_code or "UNKNOWN",
                            soc_title=soc_title or row.get(mapping["job_title"], "Unknown Occupation"),
                            normalized_title=normalized_title,
                            profession_category="Imported",
                            is_it_profession=True,
                            source_year=fiscal_year,
                        )
                        db.add(occupation)
                        db.flush()

                case = PermCase(
                    case_number=case_number,
                    employer_id=employer.id,
                    fiscal_year=int(row.get(mapping["fiscal_year"]) or fiscal_year),
                    case_status=str(row[mapping["case_status"]]).strip().upper().replace(" ", "-"),
                    filing_date=pd.to_datetime(row.get(mapping["filing_date"]), errors="coerce"),
                    decision_date=pd.to_datetime(row.get(mapping["decision_date"]), errors="coerce"),
                    job_title=row.get(mapping["job_title"]),
                    occupation_id=occupation.id if occupation else None,
                    original_soc_code=soc_code or None,
                    original_soc_title=soc_title or None,
                    worksite_city=row.get(mapping["worksite_city"]),
                    worksite_state=row.get(mapping["worksite_state"]),
                    source_file=file_name,
                    source_url=source_url,
                    source_updated_at=datetime.utcnow(),
                )
                if case.filing_date is not pd.NaT and case.filing_date is not None:
                    case.filing_date = case.filing_date.date()
                else:
                    case.filing_date = None
                if case.decision_date is not pd.NaT and case.decision_date is not None:
                    case.decision_date = case.decision_date.date()
                else:
                    case.decision_date = None
                db.add(case)
                inserted += 1
            except Exception:
                rejected += 1

        record.records_processed = processed
        record.records_inserted = inserted
        record.records_rejected = rejected
        record.status = "completed"
        record.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(record)
        return record

    def _read_dataframe(self, file_name: str, content: bytes) -> pd.DataFrame:
        if file_name.lower().endswith(".csv"):
            return pd.read_csv(BytesIO(content))
        return pd.read_excel(BytesIO(content))
