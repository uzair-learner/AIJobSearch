from app.sources.base_source import BaseSource


class UscisH1BSource(BaseSource):
    source_name = "uscis_h1b"

    async def fetch(self) -> list[dict]:
        return []
