from pydantic import BaseModel


class SourceStatus(BaseModel):
    name: str
    status: str
    message: str
    jobCount: int = 0
    matchedCount: int = 0
