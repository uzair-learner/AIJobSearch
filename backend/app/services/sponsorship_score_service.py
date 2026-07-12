from dataclasses import dataclass


@dataclass
class SponsorshipScore:
    score: int
    label: str
    reasons: list[str]
    limitations: list[str]


class SponsorshipScoreService:
    def calculate(
        self,
        recent_certified_filings: int,
        certified_in_selected_occupation: int,
        recent_year_count: int,
        has_h1b_history: bool,
        explicit_job_support_count: int,
        explicit_job_denial_count: int,
        years_since_recent_activity: int | None,
        employer_match_confidence: float = 1.0,
    ) -> SponsorshipScore:
        score = 0
        reasons: list[str] = []
        limitations = [
            "Historical PERM activity does not guarantee current sponsorship availability.",
            "Rule-based scoring is a heuristic and not legal advice.",
        ]

        if explicit_job_support_count > 0:
            score += 30
            reasons.append("Current job postings explicitly mention sponsorship.")
        if recent_certified_filings > 0:
            score += 20
            reasons.append("Certified PERM activity exists in the latest available years.")
        if certified_in_selected_occupation >= 5:
            score += 15
            reasons.append("Multiple certified filings exist in the selected occupation.")
        if recent_year_count >= 3:
            score += 10
            reasons.append("Employer filed across several recent fiscal years.")
        if has_h1b_history:
            score += 10
            reasons.append("Employer has H-1B sponsorship history.")
        if explicit_job_denial_count > 0:
            score -= 50
            reasons.append("A current job explicitly states sponsorship is unavailable.")
        if years_since_recent_activity is not None and years_since_recent_activity >= 5:
            score -= 20
            reasons.append("No PERM activity appeared in the last five years.")
        if employer_match_confidence < 0.8:
            score -= 15
            reasons.append("Employer name matching confidence is lower than preferred.")

        score = max(0, min(100, score))
        if score >= 75:
            label = "Strong recent PERM history"
        elif score >= 55:
            label = "Moderate recent PERM history"
        elif score >= 35:
            label = "Limited recent PERM history"
        elif score > 0:
            label = "Historical activity only"
        else:
            label = "No recent evidence"
        return SponsorshipScore(score=score, label=label, reasons=reasons, limitations=limitations)
