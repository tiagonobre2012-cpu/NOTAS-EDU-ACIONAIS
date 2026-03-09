from typing import Iterable


def calculate_average(note_1, note_2, note_3, recovery_note):
    regular_notes = [n for n in [note_1, note_2, note_3] if n is not None]
    regular_average = sum(regular_notes) / len(regular_notes) if regular_notes else 0.0
    base = recovery_note if recovery_note is not None else regular_average
    return round(min(base, 10.0), 2)


def calculate_status(average: float):
    if average < 6:
        return "FAILED"
    if average < 8:
        return "RECOVERY"
    return "APPROVED"


def normalize_name(value: str):
    return " ".join(value.upper().split())


def deduplicate(values: Iterable[str]):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result
