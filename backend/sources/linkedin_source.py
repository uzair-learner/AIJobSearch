from sources.base_source import JobSource, SourceSearchResult


class LinkedInSource(JobSource):
    source_name = "LinkedIn"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        return SourceSearchResult(
            name=self.source_name,
            status="unavailable",
            message="LinkedIn live results are disabled until an official API or approved partner connector is configured.",
        )
