import asyncio
from typing import List

from config import LEVER_COMPANIES
from models.job_result import JobResult
from sources.base_source import JobSource, SourceSearchResult
from utils.http_client import fetch_json_safe
from utils.search_matcher import matches_search_text


class LeverSource(JobSource):
    source_name = "Lever"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        jobs: List[JobResult] = []
        errors: list[str] = []
        tasks = [
            asyncio.to_thread(
                fetch_json_safe,
                f"https://api.lever.co/v0/postings/{company}?mode=json",
            )
            for company in LEVER_COMPANIES
        ]
        results = await asyncio.gather(*tasks)

        for company, result in zip(LEVER_COMPANIES, results):
            payload, error = result
            if error:
                errors.append(f"{company}: {error}")
                continue

            for item in payload:
                title = item.get("text", "").strip()
                categories = item.get("categories", {})
                location = categories.get("location") or "Location not listed"
                commitment = categories.get("commitment") or ""
                description = " ".join(
                    value for value in [title, commitment, location] if value
                )

                job = JobResult(
                    title=title,
                    company=company.title(),
                    location=location,
                    source=f"Lever ({company})",
                    url=item.get("hostedUrl", ""),
                    description=description,
                    datePosted=None,
                )

                if self._matches_live_query(job, query, filters):
                    jobs.append(job)

        if jobs:
            return SourceSearchResult(
                name=self.source_name,
                jobs=jobs,
                status="ok",
                message=f"Fetched live jobs from {len(LEVER_COMPANIES)} Lever companies.",
            )

        message = "No live Lever jobs matched the current search."
        if errors and len(errors) == len(LEVER_COMPANIES):
            message = "Lever companies could not be reached from this environment."

        return SourceSearchResult(
            name=self.source_name,
            jobs=[],
            status="ok" if len(errors) < len(LEVER_COMPANIES) else "warning",
            message=message,
        )

    def _matches_live_query(self, job: JobResult, query: str, filters: dict) -> bool:
        haystack = f"{job.title} {job.company} {job.location} {job.description}"
        return matches_search_text(query, haystack)
