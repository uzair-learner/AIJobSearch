from app.utils.text_normalizer import normalize_employer_name


class EmployerMatchingService:
    def normalize(self, employer_name: str) -> str:
        return normalize_employer_name(employer_name)

    def match_confidence(self, source_name: str, candidate_name: str) -> float:
        source = normalize_employer_name(source_name)
        candidate = normalize_employer_name(candidate_name)
        if source == candidate:
            return 1.0
        if source in candidate or candidate in source:
            return 0.9
        source_tokens = set(source.split())
        candidate_tokens = set(candidate.split())
        intersection = len(source_tokens & candidate_tokens)
        union = len(source_tokens | candidate_tokens) or 1
        return round(intersection / union, 2)
