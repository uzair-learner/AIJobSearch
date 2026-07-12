from app.sources.base_source import BaseSource


class AdzunaSource(BaseSource):
    source_name = "adzuna"

    async def fetch(self) -> list[dict]:
        return []
