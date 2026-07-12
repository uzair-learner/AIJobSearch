export interface SponsorSearchRequest {
  searchText: string;
  fiscalYears: number[];
  professionIds: number[];
  states: string[];
  caseStatuses: string[];
  minimumFilings: number;
  evidenceType: string;
  dateRecency: string;
  page: number;
  pageSize: number;
  sortBy: string;
  sortDirection: "asc" | "desc";
  resultView: "employers" | "filings";
}

export interface DatabaseSummary {
  databaseType: string;
  demoSeedEnabled: boolean;
  officialPermDataImported: boolean;
  employers: number;
  occupations: number;
  permCases: number;
  currentJobs: number;
  imports: number;
  availableFiscalYears: number[];
  availableStates: string[];
  availableOccupations: Array<{ socCode: string; socTitle: string }>;
}

export interface MatchingFilingItem {
  caseNumber: string;
  jobTitle: string | null;
  socCode: string | null;
  occupation: string | null;
  fiscalYear: number;
  caseStatus: string;
  filingDate: string | null;
  decisionDate: string | null;
  worksiteCity: string | null;
  worksiteState: string | null;
  offeredWage: number | null;
  wageUnit: string | null;
  source: string | null;
}

export interface SponsorSearchItem {
  employerId: number;
  employerName: string;
  normalizedEmployerName: string;
  fiscalYear: number;
  numberOfPermFilings: number;
  numberCertified: number;
  numberDenied: number;
  numberWithdrawn: number;
  certificationRate: number;
  primaryOccupation: string | null;
  socCode: string | null;
  topJobTitle: string | null;
  worksiteCity: string | null;
  worksiteState: string | null;
  offeredWage: number | null;
  wageUnit: string | null;
  filingDate: string | null;
  decisionDate: string | null;
  caseStatus: string | null;
  dataSource: string;
  dataUpdatedDate: string | null;
  currentJobCount: number;
  currentSponsoredJobCount: number;
  h1bSponsorshipHistory: boolean;
  sponsorshipConfidenceLevel: string;
  sponsorshipScore: number;
  sponsorshipReasons: string[];
  dataLimitations: string[];
  matchingFilings: MatchingFilingItem[];
}

export interface FilingSearchItem {
  employerId: number;
  employerName: string;
  caseNumber: string;
  jobTitle: string | null;
  socCode: string | null;
  occupation: string | null;
  fiscalYear: number;
  caseStatus: string;
  filingDate: string | null;
  decisionDate: string | null;
  worksiteCity: string | null;
  worksiteState: string | null;
  offeredWage: number | null;
  wageUnit: string | null;
  source: string | null;
}

export interface SponsorSearchResponse {
  page: number;
  pageSize: number;
  totalRecords: number;
  totalPages: number;
  resultView: "employers" | "filings";
  totalMatchingEmployers: number;
  totalMatchingPermCases: number;
  generatedAt: string;
  results: Array<SponsorSearchItem | FilingSearchItem>;
}

export interface EmployerDetail {
  id: number;
  employerName: string;
  alternateEmployerNames: string[];
  headquartersOrFilingLocations: string[];
  totalPermFilings: number;
  mostRecentFilingYear: number | null;
  mostRecentFilingDate: string | null;
  certifiedCases: number;
  deniedCases: number;
  withdrawnCases: number;
  certificationRate: number;
  numberOfDistinctOccupations: number;
  numberOfDistinctLocations: number;
  h1bFilingHistory: Array<Record<string, number>>;
  currentJobOpenings: number;
  currentOpeningsMentioningSponsorship: number;
  sponsorshipIndicator: string;
  sponsorshipScore: number;
  sponsorshipReasons: string[];
  dataLimitations: string[];
  charts: EmployerStatistics;
}

export interface PermCaseItem {
  caseNumber: string;
  fiscalYear: number;
  caseStatus: string;
  filingDate: string | null;
  decisionDate: string | null;
  jobTitle: string | null;
  socCode: string | null;
  socTitle: string | null;
  worksiteCity: string | null;
  worksiteState: string | null;
  offeredWageFrom: number | null;
  wageUnit: string | null;
  sourceFile: string | null;
  sourceUrl: string | null;
}

export interface EmployerOccupation {
  occupationId: number;
  socCode: string;
  socTitle: string;
  professionCategory: string | null;
  filingCount: number;
}

export interface EmployerStatistics {
  filingsByFiscalYear: Array<Record<string, string | number>>;
  outcomesByYear: Array<Record<string, string | number>>;
  topOccupations: Array<Record<string, string | number>>;
  topJobTitles: Array<Record<string, string | number>>;
  topStates: Array<Record<string, string | number>>;
  averageSalaryByYear: Array<Record<string, string | number>>;
  currentJobsByLocation: Array<Record<string, string | number>>;
}
