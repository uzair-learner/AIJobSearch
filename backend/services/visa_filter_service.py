from dataclasses import dataclass
from typing import List

from models.job_result import JobResult
from utils.text_cleaner import normalize_text


@dataclass
class VisaEvaluation:
    is_match: bool
    reason: str
    keywords: List[str]
    score: int


class VisaFilterService:
    POSITIVE_SIGNALS = {
        "h1b": 5,
        "h-1b": 5,
        "h1-b": 5,
        "h-1b transfer": 5,
        "tn visa": 5,
        "nafta professional": 5,
        "visa sponsorship": 3,
        "sponsor visa": 3,
        "sponsorship available": 3,
        "work visa sponsorship": 3,
        "employer sponsorship": 3,
        "will sponsor": 3,
        "open to sponsorship": 3,
    }

    NEGATIVE_SIGNALS = {
        "no sponsorship": -10,
        "unable to sponsor": -10,
        "cannot sponsor": -10,
        "without sponsorship": -10,
        "no visa sponsorship": -10,
        "we do not sponsor": -10,
        "requires us citizenship": -10,
        "green card only": -10,
        "gc only": -10,
        "usc only": -10,
    }

    VISA_FILTER_MAP = {
        "H1B sponsorship": ["h1b", "h-1b", "h1-b", "h-1b transfer"],
        "TN visa": ["tn visa", "nafta professional"],
        "H1B or TN": ["h1b", "h-1b", "h1-b", "h-1b transfer", "tn visa", "nafta professional"],
    }

    def evaluate_job(self, job: JobResult, visa_filter: str = "Any") -> VisaEvaluation:
        haystack = normalize_text(f"{job.title} {job.description}")
        detected_keywords: List[str] = []
        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for keyword, value in self.POSITIVE_SIGNALS.items():
            if keyword in haystack:
                detected_keywords.append(keyword)
                positive_hits.append(keyword)
                score += value

        for keyword, value in self.NEGATIVE_SIGNALS.items():
            if keyword in haystack:
                detected_keywords.append(keyword)
                negative_hits.append(keyword)
                score += value

        if negative_hits:
            return VisaEvaluation(
                is_match=False,
                reason=f"Rejected because the job mentions a negative visa signal: {negative_hits[0]}",
                keywords=detected_keywords,
                score=score,
            )

        if visa_filter in self.VISA_FILTER_MAP:
            required_keywords = self.VISA_FILTER_MAP[visa_filter]
            if not any(keyword in haystack for keyword in required_keywords):
                return VisaEvaluation(
                    is_match=False,
                    reason=f"Rejected because it does not mention {visa_filter}",
                    keywords=detected_keywords,
                    score=score,
                )

        if score > 0:
            reason = "Job description mentions visa support"
            if any(keyword in positive_hits for keyword in ["h1b", "h-1b", "h1-b", "h-1b transfer"]):
                reason = "Job description mentions H1B sponsorship"
            elif any(keyword in positive_hits for keyword in ["tn visa", "nafta professional"]):
                reason = "Job description mentions TN visa eligibility"

            return VisaEvaluation(
                is_match=True,
                reason=reason,
                keywords=detected_keywords,
                score=score,
            )

        return VisaEvaluation(
            is_match=False,
            reason="Rejected because no sponsorship-related keywords were found",
            keywords=detected_keywords,
            score=score,
        )
