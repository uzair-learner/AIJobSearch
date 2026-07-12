def average_salary(value_from: float | None, value_to: float | None) -> float | None:
    if value_from is None and value_to is None:
        return None
    if value_from is None:
        return value_to
    if value_to is None:
        return value_from
    return round((value_from + value_to) / 2, 2)
