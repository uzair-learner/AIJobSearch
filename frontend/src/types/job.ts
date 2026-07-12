export interface JobSearchRequest {
  searchText: string;
  employerIds: number[];
  professionIds: number[];
  states: string[];
  sponsorshipClassifications: string[];
  postedWithinDays: number;
  page: number;
  pageSize: number;
}

export interface JobSearchItem {
  id: number;
  employerId: number;
  employerName: string;
  title: string;
  source: string;
  sourceUrl: string;
  city: string | null;
  state: string | null;
  remoteType: string | null;
  employmentType: string | null;
  postedDate: string | null;
  sponsorshipClassification: string;
  sponsorshipScore: number;
  sponsorshipReasons: string[];
}

export interface JobSearchResponse {
  page: number;
  pageSize: number;
  totalRecords: number;
  totalPages: number;
  results: JobSearchItem[];
}
