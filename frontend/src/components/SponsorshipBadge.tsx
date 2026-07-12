export default function SponsorshipBadge({ label, score }: { label: string; score?: number }) {
  const tone =
    score && score >= 75 ? "success" : score && score >= 50 ? "warning" : score === 0 ? "muted" : "info";
  return <span className={`badge ${tone}`}>{score !== undefined ? `${label} (${score})` : label}</span>;
}
