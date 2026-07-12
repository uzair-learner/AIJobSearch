from utils.text_cleaner import normalize_text


ROLE_SYNONYMS = {
    "tech": ["technical", "technology", "software", "engineering"],
    "lead": ["leader", "principal", "senior", "manager", "head"],
    "developer": ["engineer", "programmer", "software"],
    "engineer": ["developer", "software", "platform"],
    "manager": ["lead", "head", "director"],
}

PHRASE_SYNONYMS = {
    "tech lead": [
        "technical lead",
        "engineering manager",
        "lead engineer",
        "software lead",
        "tech lead",
    ],
    "software developer": [
        "software engineer",
        "application developer",
        "developer",
    ],
}


def matches_search_text(query: str, haystack: str) -> bool:
    normalized_query = normalize_text(query)
    normalized_haystack = normalize_text(haystack)

    if not normalized_query:
        return True

    if normalized_query in normalized_haystack:
        return True

    if normalized_query in PHRASE_SYNONYMS:
        phrases = PHRASE_SYNONYMS[normalized_query]
        if any(phrase in normalized_haystack for phrase in phrases):
            return True

    terms = [term for term in normalized_query.split(" ") if term]
    if terms and all(_term_matches(term, normalized_haystack) for term in terms):
        return True

    return False


def _term_matches(term: str, haystack: str) -> bool:
    if term in haystack:
        return True

    synonyms = ROLE_SYNONYMS.get(term, [])
    return any(synonym in haystack for synonym in synonyms)
