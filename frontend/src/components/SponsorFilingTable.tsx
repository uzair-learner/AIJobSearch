import type { FilingSearchItem } from "../types/sponsor";

function formatDate(value: string | null): string {
  return value ? new Date(`${value}T00:00:00`).toLocaleDateString() : "N/A";
}

function formatWage(filing: FilingSearchItem): string {
  if (filing.offeredWage === null) return "N/A";
  return `${filing.offeredWage.toLocaleString(undefined, { maximumFractionDigits: 2 })}${filing.wageUnit ? ` / ${filing.wageUnit}` : ""}`;
}

export default function SponsorFilingTable({ filings }: { filings: FilingSearchItem[] }) {
  return (
    <div className="table-wrap panel">
      <table>
        <thead>
          <tr>
            <th>Employer</th>
            <th>Case number</th>
            <th>Job title</th>
            <th>SOC code</th>
            <th>Occupation</th>
            <th>FY</th>
            <th>Status</th>
            <th>Filing date</th>
            <th>Decision date</th>
            <th>Worksite</th>
            <th>Offered wage</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {filings.map((filing) => (
            <tr key={filing.caseNumber}>
              <td>{filing.employerName}</td>
              <td>{filing.caseNumber}</td>
              <td>{filing.jobTitle ?? "N/A"}</td>
              <td>{filing.socCode ?? "N/A"}</td>
              <td>{filing.occupation ?? "N/A"}</td>
              <td>{filing.fiscalYear}</td>
              <td>{filing.caseStatus}</td>
              <td>{formatDate(filing.filingDate)}</td>
              <td>{formatDate(filing.decisionDate)}</td>
              <td>{[filing.worksiteCity, filing.worksiteState].filter(Boolean).join(", ") || "N/A"}</td>
              <td>{formatWage(filing)}</td>
              <td>{filing.source ?? "N/A"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
