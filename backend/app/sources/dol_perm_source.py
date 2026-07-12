from app.sources.base_source import BaseSource


class DolPermSource(BaseSource):
    source_name = "dol_perm"

    async def fetch(self) -> list[dict]:
        return []
