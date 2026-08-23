# What I checked, and what the agent got wrong

## What the agent got wrong

The agent's first pass at `car_wear()` in `fleet_report.py` quietly defaulted a car with
no `last_service_km` reading to 0% wear, the same "unknown = not worn" choice it made in
`needs_service()`. That's a reasonable default, but it's still a judgment call the agent
made on its own rather than something the tests forced it into — a different, equally
defensible choice would have been to exclude that car from the average entirely instead
of folding it in at 0%. I let it stand because it matches the intent of
`needs_service()` (never falsely flag on missing data) and because `verify.py`'s average
check only cares that the report doesn't crash, not what an unread car scores. But it's
a place I'd push back if Fleet Ops later says an unread car should count differently.

The agent also initially proposed a risk score in `analyze.py` before actually checking
which columns separated the two groups — it would have been easy to just throw
`odometer_km` and `age_years` in because they "sound" predictive. I made it run the
effect-size comparison (Cohen's d, not just eyeballing group means) before it wrote the
score, and that's what caught that mileage and age carry basically zero signal here.

## What I checked before I accepted its work

I didn't take "tests pass" as good enough on its own. Before accepting anything I:
- Ran `pytest -v` and read the failure messages myself, not just the pass/fail count.
- Reproduced the `fleet_report.py` KeyError crash by hand in the interpreter before the
  fix, and re-ran it after, to see the crash actually go away rather than just trusting
  a green test.
- Reproduced the `km_to_miles(100)` bug by hand (it returned 160.9 instead of ~62.1)
  before any fix touched `fleet_utils.py`.
- Ran `python verify.py` after every batch of changes and read every line of output, not
  just the final "N of 11 checks pass" summary. It explicitly checks
  `SERVICE_INTERVAL_KM == 15000` and `WARN_AT_PERCENT == 80` in the code AND
  `settings.cfg`, so I used that as the source of truth for "untouched," not my own
  memory of what I typed.
- Diffed every changed file against the original before and after, so nothing slipped in
  outside what was asked (no scope creep into the dead code or the duplicate `is_due()`
  in `fleet_utils.py` — those were flagged, not deleted, until we decide together).

## What the data actually said

`km_since_service`, `avg_daily_km`, and `load_factor` all separate the cars that broke
down from the ones that didn't — cars that broke down averaged about twice the distance
since their last service, and ran with noticeably higher daily mileage and load. Total
`odometer_km` and `age_years`, the two columns that look obviously relevant, had almost
zero effect size (Cohen's d near 0, correlation near 0) — an older or higher-mileage car
was no more likely to break down than a newer, lower-mileage one in this dataset. The
"older, higher-mileage cars break down" assumption doesn't hold here; what matters is how
overdue and how hard-worked a car is, not how much total distance it's ever covered.
