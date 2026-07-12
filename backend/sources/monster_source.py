from sources.base_source import JobSource, SourceSearchResult


class MonsterSource(JobSource):
    source_name = "Monster"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        return SourceSearchResult(
            name=self.source_name,
            status="unavailable",
            message="Monster live results are disabled until an official API or approved partner connector is configured.",
        )
