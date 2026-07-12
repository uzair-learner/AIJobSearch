import asyncio
from typing import List

from config import USAJOBS_API_KEY, USAJOBS_USER_AGENT
from models.job_result import JobResult
from sources.base_source import JobSource, SourceSearchResult
from utils.http_client import fetch_json_safe


class USAJobsSource(JobSource):
    source_name = "USAJOBS"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        if not USAJOBS_API_KEY or not USAJOBS_USER_AGENT:
            return SourceSearchResult(
                name=self.source_name,
                status="unavailable",
                message="USAJOBS live API requires USAJOBS_API_KEY and USAJOBS_USER_AGENT.",
            )

        params = []
        if query:
            params.append(f"Keyword={query.replace(' ', '%20')}")
        params.append("ResultsPerPage=25")
        url = "https://data.usajobs.gov/api/search?" + "&".join(params)
        payload, error = await asyncio.to_thread(
            fetch_json_safe,
            url,
            {
                "Authorization-Key": USAJOBS_API_KEY,
                "User-Agent": USAJOBS_USER_AGENT,
                "Host": "data.usajobs.gov",
            },
        )
        if error:
            return SourceSearchResult(
                name=self.source_name,
                status="warning",
                message=f"USAJOBS API request failed: {error}",
            )

        items = (
            payload.get("SearchResult", {})
            .get("SearchResultItems", [])
        )
        jobs: List[JobResult] = []
        for item in items:
            descriptor = item.get("MatchedObjectDescriptor", {})
            locations = descriptor.get("PositionLocationDisplay", "Location not listed")
            if isinstance(locations, list):
                locations = ", ".join(locations)

            jobs.append(
                JobResult(
                    title=descriptor.get("PositionTitle", ""),
                    company=descriptor.get("OrganizationName", "USAJOBS"),
                    location=locations or "Location not listed",
                    source="USAJOBS",
                    url=descriptor.get("PositionURI", ""),
                    description=descriptor.get("UserArea", {})
                    .get("Details", {})
                    .get("JobSummary", ""),
                    datePosted=descriptor.get("PublicationStartDate", "")[:10] or None,
                )
            )

        return SourceSearchResult(
            name=self.source_name,
            jobs=jobs,
            status="ok",
            message=f"Fetched {len(jobs)} live USAJOBS postings.",
        )
