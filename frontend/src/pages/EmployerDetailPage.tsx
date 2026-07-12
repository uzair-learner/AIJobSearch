import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getEmployerDetail, getEmployerOccupations, getEmployerPermCases } from "../api/sponsorApi";
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";
import SponsorshipBadge from "../components/SponsorshipBadge";

export default function EmployerDetailPage() {
  const { employerId = "" } = useParams();
  const detailQuery = useQuery({ queryKey: ["employer", employerId], queryFn: () => getEmployerDetail(employerId) });
  const permCasesQuery = useQuery({ queryKey: ["employer-perm-cases", employerId], queryFn: () => getEmployerPermCases(employerId) });
  const occupationsQuery = useQuery({
    queryKey: ["employer-occupations", employerId],
    queryFn: () => getEmployerOccupations(employerId),
  });

  if (detailQuery.isLoading || permCasesQuery.isLoading || occupationsQuery.isLoading) {
    return <LoadingState label="Loading employer details..." />;
  }
  if (detailQuery.isError) {
    return <ErrorState message={(detailQuery.error as Error).message} />;
  }

  const detail = detailQuery.data!;
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Employer Details</p>
          <h1>{detail.employerName}</h1>
        </div>
        <SponsorshipBadge label={detail.sponsorshipIndicator} score={detail.sponsorshipScore} />
      </header>

      <div className="grid three">
        <article className="panel">
          <h2>Summary</h2>
          <p>Total PERM filings: {detail.totalPermFilings}</p>
          <p>Most recent filing year: {detail.mostRecentFilingYear ?? "N/A"}</p>
          <p>Certified cases: {detail.certifiedCases}</p>
          <p>Denied cases: {detail.deniedCases}</p>
          <p>Withdrawn cases: {detail.withdrawnCases}</p>
          <p>Current job openings: {detail.currentJobOpenings}</p>
        </article>
        <article className="panel">
          <h2>Aliases</h2>
          {detail.alternateEmployerNames.length ? (
            <ul>
              {detail.alternateEmployerNames.map((name) => (
                <li key={name}>{name}</li>
              ))}
            </ul>
          ) : (
            <p>No aliases recorded.</p>
          )}
        </article>
        <article className="panel">
          <h2>Data limitations</h2>
          <ul>
            {detail.dataLimitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </div>

      <div className="grid two">
        <article className="panel">
          <h2>Top occupations</h2>
          <ul>
            {occupationsQuery.data?.map((occupation) => (
              <li key={occupation.occupationId}>
                {occupation.socTitle} ({occupation.socCode}) - {occupation.filingCount}
              </li>
            ))}
          </ul>
        </article>
        <article className="panel">
          <h2>Scoring reasons</h2>
          <ul>
            {detail.sponsorshipReasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </article>
      </div>

      <article className="panel">
        <h2>PERM cases</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Case</th>
                <th>FY</th>
                <th>Status</th>
                <th>Job title</th>
                <th>Location</th>
              </tr>
            </thead>
            <tbody>
              {permCasesQuery.data?.map((item) => (
                <tr key={item.caseNumber}>
                  <td>{item.caseNumber}</td>
                  <td>{item.fiscalYear}</td>
                  <td>{item.caseStatus}</td>
                  <td>{item.jobTitle ?? "N/A"}</td>
                  <td>{item.worksiteCity}, {item.worksiteState}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
