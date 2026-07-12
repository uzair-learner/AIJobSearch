from app.sources.base_source import BaseSource


class CompanyCareerSource(BaseSource):
    source_name = "company_career"

    async def fetch(self) -> list[dict]:
        return []
