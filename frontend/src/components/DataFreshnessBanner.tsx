export default function DataFreshnessBanner({
  latestGovernmentImport,
  reportingPeriod,
  latestCurrentJobsRetrieval,
}: {
  latestGovernmentImport?: string | null;
  reportingPeriod?: string | null;
  latestCurrentJobsRetrieval?: string | null;
}) {
  return (
    <section className="banner">
      <div>
        <strong>Latest imported government data</strong>
        <span>{latestGovernmentImport ? new Date(latestGovernmentImport).toLocaleString() : "Not available yet"}</span>
      </div>
      <div>
        <strong>Reporting period</strong>
        <span>{reportingPeriod ?? "Unknown"}</span>
      </div>
      <div>
        <strong>Current job retrieval</strong>
        <span>{latestCurrentJobsRetrieval ? new Date(latestCurrentJobsRetrieval).toLocaleString() : "Not available yet"}</span>
      </div>
    </section>
  );
}
