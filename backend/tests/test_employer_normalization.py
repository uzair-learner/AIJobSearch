from app.utils.text_normalizer import normalize_employer_name


def test_employer_normalization_handles_suffixes() -> None:
    assert normalize_employer_name("Microsoft Corporation, Redmond") == "MICROSOFT CORP REDMOND"
