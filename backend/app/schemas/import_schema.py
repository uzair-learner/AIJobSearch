from pydantic import BaseModel


class DataImportResponse(BaseModel):
    id: int
    sourceName: str
    sourceUrl: str | None
    fiscalYear: int | None
    reportingPeriod: str | None
    fileName: str
    fileHash: str
    status: str
    recordsProcessed: int
    recordsInserted: int
    recordsUpdated: int
    recordsRejected: int
    startedAt: str
    completedAt: str | None
    errorMessage: str | None


class ImportFromSourceRequest(BaseModel):
    sourceUrl: str
    fiscalYear: int
    reportingPeriod: str = "Year to date"
