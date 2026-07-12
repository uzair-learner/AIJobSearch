from sources.base_source import JobSource, SourceSearchResult


class WorkopolisSource(JobSource):
    source_name = "Workopolis"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        return SourceSearchResult(
            name=self.source_name,
            status="unavailable",
            message="Workopolis live results are disabled until an official API or approved partner connector is configured.",
        )
