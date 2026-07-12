import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { searchJobs } from "../api/jobApi";
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import SponsorshipBadge from "../components/SponsorshipBadge";

export default function CurrentJobsPage() {
  const [payload] = useState({
    searchText: "",
    employerIds: [],
    professionIds: [],
    states: [],
    sponsorshipClassifications: [],
    postedWithinDays: 30,
    page: 1,
    pageSize: 20,
  });
  const jobsQuery = useQuery({ queryKey: ["current-jobs", payload], queryFn: () => searchJobs(payload) });

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Current Sponsored Jobs</p>
          <h1>Current jobs are evaluated separately from historical PERM evidence.</h1>
        </div>
      </header>

      {jobsQuery.isLoading ? <LoadingState label="Loading current jobs..." /> : null}
      {jobsQuery.isError ? <ErrorState message={(jobsQuery.error as Error).message} /> : null}
      {!jobsQuery.isLoading && !jobsQuery.isError && jobsQuery.data?.results.length === 0 ? (
        <EmptyState message="No current jobs were found." />
      ) : null}

      <div className="card-grid">
        {jobsQuery.data?.results.map((job) => (
          <article className="panel sponsor-card" key={job.id}>
            <div className="card-header">
              <div>
                <h3>{job.title}</h3>
                <p>{job.employerName}</p>
              </div>
              <SponsorshipBadge label={job.sponsorshipClassification} score={job.sponsorshipScore} />
            </div>
            <p>{job.city}, {job.state}</p>
            <ul>
              {job.sponsorshipReasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
            <a href={job.sourceUrl} target="_blank" rel="noreferrer">
              Open source
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}
