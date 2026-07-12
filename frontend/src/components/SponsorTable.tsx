import { Fragment, useState } from "react";
import { Link } from "react-router-dom";
import type { MatchingFilingItem, SponsorSearchItem } from "../types/sponsor";
import SponsorshipBadge from "./SponsorshipBadge";

function formatDate(value: string | null): string {
  return value ? new Date(`${value}T00:00:00`).toLocaleDateString() : "N/A";
}

function formatWage(filing: MatchingFilingItem): string {
  if (filing.offeredWage === null) return "N/A";
  return `${filing.offeredWage.toLocaleString(undefined, { maximumFractionDigits: 2 })}${filing.wageUnit ? ` / ${filing.wageUnit}` : ""}`;
}

export default function SponsorTable({ sponsors }: { sponsors: SponsorSearchItem[] }) {
  const [expandedEmployers, setExpandedEmployers] = useState<number[]>([]);

  function toggleEmployer(employerId: number) {
    setExpandedEmployers((current) =>
      current.includes(employerId) ? current.filter((value) => value !== employerId) : [...current, employerId]
    );
  }

  return (
    <div className="table-wrap panel">
      <table>
        <thead>
          <tr>
            <th>Employer</th>
            <th>FY</th>
            <th>PERM filings</th>
            <th>Certified</th>
            <th>Occupation</th>
            <th>Current jobs</th>
            <th>Confidence</th>
            <th>Details</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {sponsors.map((sponsor) => {
            const expanded = expandedEmployers.includes(sponsor.employerId);
            return (
              <Fragment key={sponsor.employerId}>
                <tr key={sponsor.employerId}>
                  <td>
                    <strong>{sponsor.employerName}</strong>
                    <div className="subtext">{sponsor.worksiteCity}, {sponsor.worksiteState}</div>
                  </td>
                  <td>{sponsor.fiscalYear}</td>
                  <td>{sponsor.numberOfPermFilings}</td>
                  <td>{sponsor.numberCertified}</td>
                  <td>{sponsor.primaryOccupation ?? "N/A"}</td>
                  <td>{sponsor.currentJobCount}</td>
                  <td>
                    <SponsorshipBadge label={sponsor.sponsorshipConfidenceLevel} score={sponsor.sponsorshipScore} />
                  </td>
                  <td>
                    <button type="button" className="link-button" onClick={() => toggleEmployer(sponsor.employerId)}>
                      {expanded ? "Hide filings" : `View filings (${sponsor.matchingFilings.length})`}
                    </button>
                  </td>
                  <td>
                    <Link to={`/employers/${sponsor.employerId}`}>View Employer</Link>
                  </td>
                </tr>
                {expanded ? (
                  <tr>
                    <td colSpan={9}>
                      <div className="nested-table-wrap">
                        <table>
                          <thead>
                            <tr>
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
                            {sponsor.matchingFilings.map((filing) => (
                              <tr key={filing.caseNumber}>
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
                    </td>
                  </tr>
                ) : null}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
