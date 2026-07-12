import re

LEGAL_SUFFIXES = {
    " INCORPORATED ": " INC ",
    " CORPORATION ": " CORP ",
    " COMPANY ": " CO ",
    " LIMITED ": " LTD ",
}


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_employer_name(value: str) -> str:
    normalized = f" {value.upper()} "
    normalized = re.sub(r"[^A-Z0-9 ]", " ", normalized)
    for source, replacement in LEGAL_SUFFIXES.items():
        normalized = normalized.replace(source, replacement)
    return normalize_whitespace(normalized)


def normalize_title(value: str) -> str:
    return normalize_whitespace(re.sub(r"[^A-Za-z0-9 ]", " ", value).upper())
