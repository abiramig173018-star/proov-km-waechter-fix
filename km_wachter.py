# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return the percent of the service interval used up (not floored)."""
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True once a car has used up WARN_AT_PERCENT of its interval.

    A car with no last-service reading is unknown, not fully worn, so it
    is never flagged from a missing reading alone.
    """
    last = car.get("last_service_km")
    if last is None:
        return False
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Print and return the ids of every car that needs a service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
