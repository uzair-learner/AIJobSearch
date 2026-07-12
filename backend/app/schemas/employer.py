from pydantic import BaseModel


class EmployerSummaryResponse(BaseModel):
    id: int
    employerName: str
    alternateEmployerNames: list[str]
    headquartersOrFilingLocations: list[str]
    totalPermFilings: int
    mostRecentFilingYear: int | None
    mostRecentFilingDate: str | None
    certifiedCases: int
    deniedCases: int
    withdrawnCases: int
    certificationRate: float
    numberOfDistinctOccupations: int
    numberOfDistinctLocations: int
    h1bFilingHistory: list[dict]
    currentJobOpenings: int
    currentOpeningsMentioningSponsorship: int
    sponsorshipIndicator: str
    sponsorshipScore: int
    sponsorshipReasons: list[str]
    dataLimitations: list[str]
    charts: dict


class EmployerPermCaseItem(BaseModel):
    caseNumber: str
    fiscalYear: int
    caseStatus: str
    filingDate: str | None
    decisionDate: str | None
    jobTitle: str | None
    socCode: str | None
    socTitle: str | None
    worksiteCity: str | None
    worksiteState: str | None
    offeredWageFrom: float | None
    wageUnit: str | None
    sourceFile: str | None
    sourceUrl: str | None


class EmployerOccupationItem(BaseModel):
    occupationId: int
    socCode: str
    socTitle: str
    professionCategory: str | None
    filingCount: int


class EmployerStatisticsResponse(BaseModel):
    filingsByFiscalYear: list[dict]
    outcomesByYear: list[dict]
    topOccupations: list[dict]
    topJobTitles: list[dict]
    topStates: list[dict]
    averageSalaryByYear: list[dict]
    currentJobsByLocation: list[dict]
