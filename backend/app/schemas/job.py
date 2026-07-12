from pydantic import BaseModel


class JobClassificationPreview(BaseModel):
    classification: str
    score: int
    reasons: list[str]
