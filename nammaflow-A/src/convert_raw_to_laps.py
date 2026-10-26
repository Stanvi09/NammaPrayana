"""Convert B's raw checkpoint log (one row per sensor pass) into one row per lap.

Usage (from repo root): python src/convert_raw_to_laps.py <raw.csv> <laps.csv>

Assumptions (confirm with B):
  - each train_id is one session (session_id = train_id)
  - S1 = Start checkpoint, S3 = Majestic (the delay we predict)
  - raw timestamps are in track seconds; TIME_SCALE converts to metro time
"""
import sys
import pandas as pd

TIME_SCALE = 5            # 1 s on track = 5 s metro time (change if the team picks another)
START_CP, TARGET_CP = "S1", "S3"

src = sys.argv[1] if len(sys.argv) > 1 else "data/raw_train_checkpoint_data_SIMULATED.csv"
dst = sys.argv[2] if len(sys.argv) > 2 else "data/laps_from_B_simulated.csv"

raw = pd.read_csv(src, parse_dates=["timestamp", "scheduled_time"])

# basic checks: drop duplicates, flag impossible rows
raw = raw.drop_duplicates()
raw["delay_s"] = (raw.timestamp - raw.scheduled_time).dt.total_seconds()
raw["delay_min"] = raw.delay_s * TIME_SCALE / 60          # metro minutes
raw["delay_min"] = raw.delay_min.clip(lower=0)            # early arrival = no delay

# one row per (session, lap): pivot checkpoints into columns
keys = ["train_id", "lap", "scenario"]
wide = raw.pivot_table(index=keys, columns="checkpoint_id", values="delay_min").reset_index()
wide = wide.rename(columns={START_CP: "delay_start", TARGET_CP: "delay_majestic"})

first_ts = raw[raw.checkpoint_id == START_CP].set_index(["train_id", "lap"]).timestamp
wide["hour"] = [first_ts[(t, l)].hour for t, l in zip(wide.train_id, wide.lap)]

wide = wide.rename(columns={"train_id": "session_id"}).sort_values(["session_id", "lap"])

# previous trains' delay at the target checkpoint (reset at each new session)
g = wide.groupby("session_id").delay_majestic
for k in (1, 2, 3):
    wide[f"prev{k}_delay"] = g.shift(k).fillna(0)

wide["rain_flag"] = (wide.scenario == "rain").astype(int)
wide["festival_flag"] = (wide.scenario == "festival").astype(int)

cols = ["session_id", "lap", "scenario", "hour", "rain_flag", "festival_flag",
        "delay_start", "prev1_delay", "prev2_delay", "prev3_delay", "delay_majestic"]
wide[cols].round(2).to_csv(dst, index=False)
print(wide[cols].shape, "->", dst)
print(wide[cols].head(12).to_string(index=False))
