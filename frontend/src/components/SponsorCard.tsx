import { Link } from "react-router-dom";
import type { SponsorSearchItem } from "../types/sponsor";
import SponsorshipBadge from "./SponsorshipBadge";

export default function SponsorCard({ sponsor }: { sponsor: SponsorSearchItem }) {
  return (
    <article className="panel sponsor-card">
      <div className="card-header">
        <div>
          <h3>{sponsor.employerName}</h3>
          <p>{sponsor.primaryOccupation ?? "Occupation not available"}</p>
        </div>
        <SponsorshipBadge label={sponsor.sponsorshipConfidenceLevel} score={sponsor.sponsorshipScore} />
      </div>
      <div className="stat-row">
        <span>PERM filings: {sponsor.numberOfPermFilings}</span>
        <span>Certified: {sponsor.numberCertified}</span>
        <span>Current jobs: {sponsor.currentJobCount}</span>
      </div>
      <p className="muted-text">
        Historical sponsorship evidence only. A prior filing does not guarantee current sponsorship availability.
      </p>
      <div className="button-row">
        <Link to={`/employers/${sponsor.employerId}`}>View Employer</Link>
      </div>
    </article>
  );
}
