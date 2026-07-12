import { apiGet, apiPost } from "./client";
import type {
  EmployerDetail,
  EmployerOccupation,
  EmployerStatistics,
  PermCaseItem,
  SponsorSearchRequest,
  SponsorSearchResponse,
} from "../types/sponsor";

export const searchSponsors = (payload: SponsorSearchRequest) =>
  apiPost<SponsorSearchResponse>("/sponsors/search", payload);

export const getEmployerDetail = (employerId: string) => apiGet<EmployerDetail>(`/employers/${employerId}`);
export const getEmployerPermCases = (employerId: string) => apiGet<PermCaseItem[]>(`/employers/${employerId}/perm-cases`);
export const getEmployerOccupations = (employerId: string) => apiGet<EmployerOccupation[]>(`/employers/${employerId}/occupations`);
export const getEmployerStatistics = (employerId: string) => apiGet<EmployerStatistics>(`/employers/${employerId}/statistics`);
