# analyze.py
# Make KM-Waechter smarter: rank cars by breakdown risk from their history, so the fleet team
# fixes the risky ones before the 80% rule would ever flag them.
#
# Summary: km_since_service, avg_daily_km, and load_factor separate the cars that broke down
# from those that didn't (higher in the broke-down group every time). Total odometer_km and
# age_years do NOT separate them at all -- both have almost zero correlation with breaking down.
# An "older, higher-mileage cars break down" story does not hold up in this data.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

CANDIDATE_COLUMNS = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]


def cohens_d(df: pd.DataFrame, col: str) -> float:
    """Standardized mean difference between the broke_down=1 and broke_down=0 groups.

    This is how we let the numbers answer instead of assuming: a column with |d| near 0
    does not separate the two groups; a column with a large |d| does.
    """
    healthy = df.loc[df["broke_down"] == 0, col]
    broke = df.loc[df["broke_down"] == 1, col]
    n0, n1 = len(healthy), len(broke)
    pooled_std = (
        ((n0 - 1) * healthy.std() ** 2 + (n1 - 1) * broke.std() ** 2) / (n0 + n1 - 2)
    ) ** 0.5
    return (broke.mean() - healthy.mean()) / pooled_std


print("Which columns actually separate broke-down cars from healthy ones?")
print("-" * 68)
effects = {}
for col in CANDIDATE_COLUMNS:
    d = cohens_d(df, col)
    corr = df[col].corr(df["broke_down"])
    effects[col] = d
    verdict = "separates the groups" if abs(d) >= 0.3 else "does NOT separate the groups"
    print(f"{col:18s} corr={corr:+.3f}  cohen's d={d:+.3f}  -> {verdict}")
print()

# Keep only columns that actually separate the groups (|d| >= 0.3 is a real, non-trivial effect).
# In this dataset that rules out odometer_km and age_years, and keeps km_since_service,
# avg_daily_km, and load_factor.
PREDICTIVE_COLUMNS = [col for col, d in effects.items() if abs(d) >= 0.3]

# Weight each predictive column by how strongly it separates the groups, so the column that
# matters most (km_since_service) counts for the most in the score.
weights = {col: abs(effects[col]) for col in PREDICTIVE_COLUMNS}
weight_total = sum(weights.values())
weights = {col: w / weight_total for col, w in weights.items()}

# Combine the predictive columns into one weighted z-score per car, then convert that to a
# 0-100 percentile rank across the fleet -- an easy-to-read risk score, no ML needed.
raw_score = pd.Series(0.0, index=df.index)
for col in PREDICTIVE_COLUMNS:
    z = (df[col] - df[col].mean()) / df[col].std()
    raw_score += weights[col] * z

df["risk_score"] = (raw_score.rank(pct=True) * 100).round(1)

print(f"Predictive columns used (weight): "
      + ", ".join(f"{c} ({weights[c]:.0%})" for c in PREDICTIVE_COLUMNS))
print()
print("Cars ranked by breakdown risk, highest first:")
print("-" * 68)
ranked = df.sort_values("risk_score", ascending=False)
for _, row in ranked.iterrows():
    flag = " [BROKE DOWN]" if row["broke_down"] == 1 else ""
    print(f"{row['car_id']:10s} risk={row['risk_score']:5.1f}  "
          f"km_since_service={row['km_since_service']:6.0f}  "
          f"avg_daily_km={row['avg_daily_km']:4.0f}  "
          f"load_factor={row['load_factor']:.2f}{flag}")
