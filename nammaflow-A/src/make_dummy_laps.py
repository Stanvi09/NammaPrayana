"""Dummy NammaFlow lap dataset. All delays are in metro minutes.
Run from the repo root: python src/make_dummy_laps.py
One row per lap. Target: delay_majestic.
Split by session_id, never by lap."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N_SESSIONS, LAPS = 40, 10
CARRY = 0.5  # share of last lap's delay that carries into the next

SCEN = {  # (prob of fresh delay, mean size in minutes, rain_flag, festival_flag)
    "dry":      (0.25, 2.0, 0, 0),
    "rain":     (0.45, 3.5, 1, 0),
    "festival": (0.55, 5.0, 0, 1),
}
TYPES = ["stop", "slowdown", "late_start"]
# where the fresh delay enters the track
PLACE = ["start", "mid", "majestic"]

rows = []
for s in range(N_SESSIONS):
    scenario = rng.choice(list(SCEN), p=[0.4, 0.3, 0.3])
    p, mean, rain, fest = SCEN[scenario]
    hour = int(rng.choice([8, 9, 10, 13, 17, 18, 19]))
    prev1 = prev2 = prev3 = 0.0
    for lap in range(1, LAPS + 1):
        fresh, dtype, place, rare = 0.0, "none", "none", 0
        if rng.random() < p:
            fresh = rng.exponential(mean)
            dtype = rng.choice(TYPES)
            place = rng.choice(PLACE)
            if rng.random() < 0.04:        # rare long stop -> hold out for test
                fresh = rng.uniform(10, 15)
                dtype, rare = "stop", 1
        d_start = CARRY * prev1 + (fresh if place == "start" else 0) + rng.normal(0, 0.2)
        d_mid = d_start + (fresh if place == "mid" else 0) + rng.normal(0, 0.3)
        d_maj = d_mid * 1.05 + (fresh if place == "majestic" else 0) + 0.3 * rain + rng.normal(0, 0.4)
        d_end = d_maj + rng.normal(0, 0.3)
        d_start, d_mid, d_maj, d_end = [max(0.0, round(x, 2)) for x in (d_start, d_mid, d_maj, d_end)]
        rows.append(dict(
            session_id=s, lap=lap, scenario=scenario, delay_type=dtype,
            delay_place=place, rare_long_stop=rare,
            hour=hour, rain_flag=rain, festival_flag=fest,
            delay_start=d_start, delay_mid=d_mid,
            prev1_delay=round(prev1, 2), prev2_delay=round(prev2, 2), prev3_delay=round(prev3, 2),
            delay_majestic=d_maj, delay_end=d_end,
        ))
        prev3, prev2, prev1 = prev2, prev1, d_maj

df = pd.DataFrame(rows)
df.to_csv("data/dummy_laps.csv", index=False)
print(df.shape)
print(df.groupby("scenario").delay_majestic.describe().round(2))
