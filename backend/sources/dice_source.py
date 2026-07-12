from sources.base_source import JobSource, SourceSearchResult


class DiceSource(JobSource):
    source_name = "Dice"

    async def search(self, query: str, filters: dict) -> SourceSearchResult:
        return SourceSearchResult(
            name=self.source_name,
            status="unavailable",
            message="Dice live results are disabled until an official API or approved partner connector is configured.",
        )
