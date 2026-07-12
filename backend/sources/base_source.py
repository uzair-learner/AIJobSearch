from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from models.job_result import JobResult


@dataclass
class SourceSearchResult:
    name: str
    jobs: List[JobResult] = field(default_factory=list)
    status: str = "ok"
    message: str = ""


class JobSource(ABC):
    source_name: str

    @abstractmethod
    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        pass
