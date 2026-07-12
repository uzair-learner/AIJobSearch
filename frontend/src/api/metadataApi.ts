import { apiGet } from "./client";

export const getFiscalYears = () => apiGet<Array<{ label: string; value: string | number; reportingPeriod: string | null }>>("/metadata/fiscal-years");
export const getProfessions = () => apiGet<Array<{ id: number; socCode: string; socTitle: string; professionCategory?: string }>>("/metadata/it-professions");
export const getStates = () => apiGet<string[]>("/metadata/states");
export const getCaseStatuses = () => apiGet<string[]>("/metadata/case-statuses");
export const getDataFreshness = () =>
  apiGet<{
    latestGovernmentImport: string | null;
    reportingPeriod: string | null;
    latestCurrentJobsRetrieval: string | null;
    governmentDataLabel: string;
  }>("/metadata/data-freshness");
