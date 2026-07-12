from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SponsorSearchRequest(BaseModel):
    searchText: str | None = None
    fiscalYears: list[int] = Field(default_factory=list)
    professionIds: list[int] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)
    caseStatuses: list[str] = Field(default_factory=list)
    minimumFilings: int = 1
    evidenceType: str | None = "all"
    dateRecency: str | None = "all"
    page: int = 1
    pageSize: int = 25
    sortBy: str = "recent_filings"
    sortDirection: Literal["asc", "desc"] = "desc"

    @model_validator(mode="after")
    def ensure_any_filter(self) -> "SponsorSearchRequest":
        self.searchText = self.searchText.strip() if self.searchText else None
        self.fiscalYears = [year for year in self.fiscalYears if year is not None]
        self.professionIds = [profession_id for profession_id in self.professionIds if profession_id is not None]
        self.states = [state for state in self.states if state]
        self.caseStatuses = [status for status in self.caseStatuses if status]
        self.evidenceType = self.evidenceType or "all"
        self.dateRecency = self.dateRecency or "all"
        active = any(
            [
                bool(self.searchText and self.searchText.strip()),
                bool(self.fiscalYears),
                bool(self.professionIds),
                bool(self.states),
                bool(self.caseStatuses),
                self.minimumFilings > 1,
                self.evidenceType != "all",
                self.dateRecency != "all",
            ]
        )
        if not active:
            raise ValueError("At least one search condition is required.")
        return self


class CurrentJobSearchRequest(BaseModel):
    searchText: str | None = None
    employerIds: list[int] = Field(default_factory=list)
    professionIds: list[int] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)
    sponsorshipClassifications: list[str] = Field(default_factory=list)
    postedWithinDays: int | None = 30
    page: int = 1
    pageSize: int = 25


class PaginationResponse(BaseModel):
    page: int
    pageSize: int
    totalRecords: int
    totalPages: int


class SearchResultItem(BaseModel):
    employerId: int
    employerName: str
    normalizedEmployerName: str
    fiscalYear: int
    numberOfPermFilings: int
    numberCertified: int
    numberDenied: int
    numberWithdrawn: int
    certificationRate: float
    primaryOccupation: str | None
    socCode: str | None
    topJobTitle: str | None
    worksiteCity: str | None
    worksiteState: str | None
    offeredWage: float | None
    wageUnit: str | None
    filingDate: str | None
    decisionDate: str | None
    caseStatus: str | None
    dataSource: str
    dataUpdatedDate: str | None
    currentJobCount: int
    currentSponsoredJobCount: int
    h1bSponsorshipHistory: bool
    sponsorshipConfidenceLevel: str
    sponsorshipScore: int
    sponsorshipReasons: list[str]
    dataLimitations: list[str]


class SponsorSearchResponse(PaginationResponse):
    results: list[SearchResultItem]
    generatedAt: datetime


class CurrentJobItem(BaseModel):
    id: int
    employerId: int
    employerName: str
    title: str
    source: str
    sourceUrl: str
    city: str | None
    state: str | None
    remoteType: str | None
    employmentType: str | None
    postedDate: str | None
    sponsorshipClassification: str
    sponsorshipScore: int
    sponsorshipReasons: list[str]


class CurrentJobSearchResponse(PaginationResponse):
    results: list[CurrentJobItem]
