# fleet_utils.py
# Helpers shared by the fleet report.

KM_PER_MILE = 1.60934                   # 1 mile = 1.60934 km (was miswired as a multiplier)


def km_to_miles(km: float) -> float:
    """Convert kilometers to miles for the UK partner report."""
    # Hinweis: wird vom Nachtlauf fuer den UK-Partnerbericht gebraucht. Nicht anfassen!
    # (Note: the nightly run needs this for the UK partner report. Do not touch!)
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage."""
    return f"{value:.0f}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list of numbers, or 0 for an empty list."""
    if not values:
        return 0
    return sum(values) / len(values)


def is_due(pct: float, threshold: float) -> bool:
    """Return True if pct has reached threshold.

    NOTE: this duplicates km_wachter.needs_service()'s threshold check.
    Flagged for you to decide whether to remove it in favor of one source
    of truth; left as-is for now since it wasn't part of this fix.
    """
    return pct >= threshold


def parse_service_date(text: str):
    """Parse a 'DD.MM.YYYY' date string. Unused: kept from the old garage form (2014)."""
    parts = text.split(".")
    if len(parts) != 3:
        return None
    day, month, year = (int(p) for p in parts)
    return (year, month, day)


def chunk_list(items: list, size: int) -> list:
    """Split items into chunks of size. Unused elsewhere in this codebase."""
    chunks = []
    current = []
    for item in items:
        current.append(item)
        if len(current) == size:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks
