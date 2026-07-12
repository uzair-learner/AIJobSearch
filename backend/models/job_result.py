from typing import List, Optional

from pydantic import BaseModel


class JobResult(BaseModel):
    title: str
    company: str
    location: str
    source: str
    url: str
    description: str
    isLive: bool = True
    visaMatch: bool = False
    visaReason: str = ""
    detectedVisaKeywords: List[str] = []
    datePosted: Optional[str] = None
    score: int = 0
