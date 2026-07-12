import asyncio
from typing import List

from config import GREENHOUSE_BOARDS
from models.job_result import JobResult
from sources.base_source import JobSource, SourceSearchResult
from utils.http_client import fetch_json_safe
from utils.search_matcher import matches_search_text


class GreenhouseSource(JobSource):
    source_name = "Greenhouse"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        jobs: List[JobResult] = []
        errors: list[str] = []
        tasks = [
            asyncio.to_thread(
                fetch_json_safe,
                f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
            )
            for board in GREENHOUSE_BOARDS
        ]
        results = await asyncio.gather(*tasks)

        for board, result in zip(GREENHOUSE_BOARDS, results):
            payload, error = result
            if error:
                errors.append(f"{board}: {error}")
                continue

            for item in payload.get("jobs", []):
                title = item.get("title", "").strip()
                location = item.get("location", {}).get("name", "Location not listed")
                absolute_url = item.get("absolute_url", "")
                updated_at = item.get("updated_at")

                job = JobResult(
                    title=title,
                    company=board.title(),
                    location=location,
                    source=f"Greenhouse ({board})",
                    url=absolute_url,
                    description=title,
                    datePosted=updated_at[:10] if updated_at else None,
                )

                if self._matches_live_query(job, query, filters):
                    jobs.append(job)

        if jobs:
            return SourceSearchResult(
                name=self.source_name,
                jobs=jobs,
                status="ok",
                message=f"Fetched live jobs from {len(GREENHOUSE_BOARDS)} Greenhouse boards.",
            )

        message = "No live Greenhouse jobs matched the current search."
        if errors and len(errors) == len(GREENHOUSE_BOARDS):
            message = "Greenhouse boards could not be reached from this environment."

        return SourceSearchResult(
            name=self.source_name,
            jobs=[],
            status="ok" if len(errors) < len(GREENHOUSE_BOARDS) else "warning",
            message=message,
        )

    def _matches_live_query(self, job: JobResult, query: str, filters: dict) -> bool:
        haystack = f"{job.title} {job.company} {job.location}"
        return matches_search_text(query, haystack)
