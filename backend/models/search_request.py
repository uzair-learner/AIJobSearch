from pydantic import BaseModel


class SearchRequest(BaseModel):
    searchText: str = ""
    country: str = "Any"
    jobType: str = "Any"
    technology: str = "Any"
    visaFilter: str = "Any"
