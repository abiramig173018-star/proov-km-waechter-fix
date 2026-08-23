# test_km_wachter.py
from km_wachter import needs_service, wear_percent


def test_almost_due_car_is_flagged():
    # A car at 14,900 of its 15,000 km window is about 99% worn and MUST be flagged.
    assert needs_service({"id": "VOS-4471", "odometer": 14900, "last_service_km": 0}) is True


def test_missing_reading_is_not_treated_as_zero():
    # A car with NO last-service reading must not be treated as fully worn.
    assert needs_service({"id": "VOS-7788", "odometer": 92000}) is False


def test_wear_percent_math_is_correct():
    # 14,900 of 15,000 km used is 99.33% worn, not floored down to 0% or 99%.
    assert abs(wear_percent(14900, 15000) - 99.333) < 0.01
    # Exactly one full interval used up is exactly 100%.
    assert wear_percent(15000, 15000) == 100
    # Half the interval used up is exactly 50%.
    assert wear_percent(7500, 15000) == 50
