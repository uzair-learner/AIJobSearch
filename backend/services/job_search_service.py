import asyncio
from typing import List

from models.job_result import JobResult
from models.search_request import SearchRequest
from models.source_status import SourceStatus
from services.visa_filter_service import VisaFilterService
from sources.dice_source import DiceSource
from sources.greenhouse_source import GreenhouseSource
from sources.indeed_source import IndeedSource
from sources.lever_source import LeverSource
from sources.linkedin_source import LinkedInSource
from sources.monster_source import MonsterSource
from sources.usajobs_source import USAJobsSource
from sources.workopolis_source import WorkopolisSource
from utils.text_cleaner import normalize_text


class JobSearchService:
    def __init__(self) -> None:
        self.sources = [
            GreenhouseSource(),
            LeverSource(),
            USAJobsSource(),
            IndeedSource(),
            MonsterSource(),
            WorkopolisSource(),
            DiceSource(),
            LinkedInSource(),
        ]
        self.visa_filter_service = VisaFilterService()
        self.last_used_sources: List[str] = []
        self.last_source_statuses: List[SourceStatus] = []

    async def search_jobs(self, request: SearchRequest) -> List[JobResult]:
        self.last_used_sources = [source.source_name for source in self.sources]
        tasks = [
            self._safe_search(source, request.searchText, request.model_dump())
            for source in self.sources
        ]
        source_results = await asyncio.gather(*tasks)

        filtered_jobs = []
        source_statuses: List[SourceStatus] = []

        for result in source_results:
            matched_for_source = 0

            for job in result.jobs:
                if not self._matches_filters(job, request):
                    continue

                evaluation = self.visa_filter_service.evaluate_job(job, request.visaFilter)
                job.visaMatch = evaluation.is_match
                job.visaReason = evaluation.reason
                job.detectedVisaKeywords = evaluation.keywords
                job.score = evaluation.score

                if request.country == "USA":
                    if not evaluation.is_match or evaluation.score <= 0:
                        continue

                if request.visaFilter != "Any" and not evaluation.is_match:
                    continue

                matched_for_source += 1
                filtered_jobs.append(job)

            source_statuses.append(
                SourceStatus(
                    name=result.name,
                    status=result.status,
                    message=self._build_source_message(
                        result.message,
                        result.status,
                        len(result.jobs),
                        matched_for_source,
                    ),
                    jobCount=len(result.jobs),
                    matchedCount=matched_for_source,
                )
            )

        self.last_source_statuses = source_statuses

        return sorted(filtered_jobs, key=lambda job: job.score, reverse=True)

    async def _safe_search(self, source, query: str, filters: dict):
        try:
            return await source.search(query, filters)
        except Exception as error:
            return SourceStatusProxy(
                name=source.source_name,
                status="warning",
                message=f"Source failed: {error}",
            )

    def _matches_filters(self, job: JobResult, request: SearchRequest) -> bool:
        search_blob = normalize_text(
            f"{job.title} {job.company} {job.location} {job.description}"
        )

        if request.searchText:
            normalized_query = normalize_text(request.searchText)
            query_terms = [term for term in normalized_query.split(" ") if term]

            if normalized_query not in search_blob:
                if not query_terms or not all(term in search_blob for term in query_terms):
                    return False

        if request.country != "Any":
            location = normalize_text(job.location)
            if request.country == "Remote":
                if "remote" not in location:
                    return False
            elif normalize_text(request.country) not in location:
                return False

        if request.jobType != "Any":
            if normalize_text(request.jobType) not in search_blob:
                return False

        if request.technology != "Any":
            tech = normalize_text(request.technology)
            if tech not in search_blob:
                return False

        return True

    def _build_source_message(
        self,
        base_message: str,
        status: str,
        fetched_count: int,
        matched_count: int,
    ) -> str:
        if status != "ok":
            return base_message

        if fetched_count == 0:
            return base_message

        if matched_count == 0:
            return (
                f"Fetched {fetched_count} live jobs, but none matched your current filters."
            )

        return f"Fetched {fetched_count} live jobs, and {matched_count} matched your current filters."


class SourceStatusProxy:
    def __init__(self, name: str, status: str, message: str) -> None:
        self.name = name
        self.status = status
        self.message = message
        self.jobs: List[JobResult] = []
