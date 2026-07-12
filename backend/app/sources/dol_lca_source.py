from app.sources.base_source import BaseSource


class DolLcaSource(BaseSource):
    source_name = "dol_lca"

    async def fetch(self) -> list[dict]:
        return []
