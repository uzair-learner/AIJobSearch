import { apiPost } from "./client";
import type { JobSearchRequest, JobSearchResponse } from "../types/job";

export const searchJobs = (payload: JobSearchRequest) => apiPost<JobSearchResponse>("/jobs/search", payload);
