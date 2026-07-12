import { Link } from "react-router-dom";
import type { SponsorSearchItem } from "../types/sponsor";
import SponsorshipBadge from "./SponsorshipBadge";

export default function SponsorTable({ sponsors }: { sponsors: SponsorSearchItem[] }) {
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
            <th />
          </tr>
        </thead>
        <tbody>
          {sponsors.map((sponsor) => (
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
                <Link to={`/employers/${sponsor.employerId}`}>View Employer</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
