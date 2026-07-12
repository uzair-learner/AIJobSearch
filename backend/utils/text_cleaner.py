import re


def normalize_text(value: str) -> str:
    if not value:
        return ""

    cleaned = value.lower()
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()
