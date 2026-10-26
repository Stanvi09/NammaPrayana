"""Role A: train the delay model.  Usage (from repo root): python src/train_delay_model.py data/dummy_laps.csv

What it does
  1. Locks a test set of whole sessions (written to test_sessions.txt, NOT used here)
  2. Session-wise cross-validation on the rest: 3 baselines vs the model
  3. Quantile models (10th / 90th percentile) -> an 80% range, with coverage check
  4. Ablations: remove rain/festival flags, remove previous-train delays
  5. Trains the final model on all non-test sessions and saves it
  (The model predicts the INCREASE over the last checkpoint's delay, then adds it back.
   This beat predicting the delay directly in testing.)
  6. predict_delay(): median, low, high and probable-factor tag
"""
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor as GBR
from sklearn.metrics import mean_absolute_error as mae
from sklearn.model_selection import GroupKFold

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/dummy_laps.csv"
TARGET = "delay_majestic"
FEATURES = ["delay_start", "delay_mid", "prev1_delay", "prev2_delay", "prev3_delay",
            "hour", "rain_flag", "festival_flag"]
PREV = ["prev1_delay", "prev2_delay", "prev3_delay"]
FLAGS = ["rain_flag", "festival_flag"]
FACTOR_THRESHOLD = 0.5   # metro minutes: flag must shift the prediction by this much

df = pd.read_csv(CSV)
FEATURES = [c for c in FEATURES if c in df.columns]   # delay_mid only if the track has a Mid sensor
LAST_CP = "delay_mid" if "delay_mid" in FEATURES else "delay_start"

# ---- 1. lock the test set (whole sessions) -------------------------------
sessions = np.array(sorted(df.session_id.unique()))
rng = np.random.default_rng(0)
test_sessions = rng.choice(sessions, size=max(1, len(sessions) // 5), replace=False)
pd.Series(test_sessions).to_csv("data/test_sessions.txt", index=False, header=False)
dev = df[~df.session_id.isin(test_sessions)]
if "rare_long_stop" in dev.columns:      # rare long stops are kept aside for the final test
    dev = dev[dev.rare_long_stop == 0]
dev = dev.reset_index(drop=True)
print(f"{len(dev)} dev laps ({dev.session_id.nunique()} sessions); "
      f"{len(test_sessions)} sessions locked as test, not touched.\n")

X, y, g = dev[FEATURES], dev[TARGET], dev.session_id
r = y - X[LAST_CP]          # what the model learns: increase over the last checkpoint
cv = GroupKFold(n_splits=5)


def fit(cols, loss="squared_error", alpha=None, Xd=X, yd=y):
    kw = dict(loss=loss, n_estimators=200, max_depth=3, learning_rate=0.05,
              random_state=0)
    if alpha is not None:
        kw["alpha"] = alpha
    return GBR(**kw).fit(Xd[cols], yd)


# ---- 2. baselines vs model, session-wise CV ------------------------------
def cv_mae(cols):
    scores = []
    for tr, te in cv.split(X, y, g):
        m = fit(cols, "absolute_error", Xd=X.iloc[tr], yd=r.iloc[tr])
        pred = np.maximum(0, X.iloc[te][LAST_CP] + m.predict(X.iloc[te][cols]))
        scores.append(mae(y.iloc[te], pred))
    return np.mean(scores)


results = {
    "no_delay": mae(y, np.zeros(len(y))),
    "same_delay_as_last_checkpoint": mae(y, X[LAST_CP]),
    "same_as_previous_train": mae(y, X.prev1_delay),
    "model": cv_mae(FEATURES),
}
print("CV mean absolute error (metro min)")
for k, v in results.items():
    print(f"  {k:24s} {v:.3f}")

# ---- 3. 80% range via quantile regression + coverage ---------------------
cover, width = [], []
for tr, te in cv.split(X, y, g):
    b = X.iloc[te][LAST_CP]
    lo = np.maximum(0, b + fit(FEATURES, "quantile", 0.1, X.iloc[tr], r.iloc[tr]).predict(X.iloc[te]))
    hi = np.maximum(0, b + fit(FEATURES, "quantile", 0.9, X.iloc[tr], r.iloc[tr]).predict(X.iloc[te]))
    cover.append(np.mean((y.iloc[te] >= lo) & (y.iloc[te] <= hi)))
    width.append(np.mean(hi - lo))
results["range_coverage_80"] = float(np.mean(cover))
results["range_mean_width"] = float(np.mean(width))
print(f"\n80% range covers truth {np.mean(cover):.0%} of the time "
      f"(target ~80%), mean width {np.mean(width):.2f} min")

# ---- 4. ablations ---------------------------------------------------------
abl = {
    "no_rain_festival_flags": [c for c in FEATURES if c not in FLAGS],
    "no_previous_train_delays": [c for c in FEATURES if c not in PREV],
}
print("\nAblations (CV MAE, lower is better)")
for name, cols in abl.items():
    results[name] = cv_mae(cols)
    print(f"  {name:26s} {results[name]:.3f}")

# ---- 5. final models on all dev sessions ---------------------------------
final = {
    "median": fit(FEATURES, "absolute_error", yd=r),
    "low": fit(FEATURES, "quantile", 0.1, yd=r),
    "high": fit(FEATURES, "quantile", 0.9, yd=r),
    "features": FEATURES,
    "base": LAST_CP,
}
joblib.dump(final, "models/delay_model.joblib")
json.dump(results, open("results/cv_results.json", "w"), indent=2)
print("\nSaved models/delay_model.joblib and results/cv_results.json")


# ---- 6. the function D calls ---------------------------------------------
def predict_delay(row: dict, model_path="models/delay_model.joblib"):
    """row needs the FEATURES keys. Returns metro minutes + probable factor."""
    m = joblib.load(model_path)
    x = pd.DataFrame([row])[m["features"]]
    base = float(row[m["base"]])
    mid = max(0.0, base + float(m["median"].predict(x)[0]))
    lo = min(mid, max(0.0, base + float(m["low"].predict(x)[0])))
    hi = max(mid, base + float(m["high"].predict(x)[0]))

    # probable factor: switch each flag off and see how much the prediction drops
    factor, best = "none", FACTOR_THRESHOLD
    for flag, label in [("rain_flag", "rain"), ("festival_flag", "festival")]:
        if row.get(flag, 0):
            off = pd.DataFrame([{**row, flag: 0}])[m["features"]]
            shift = mid - max(0.0, base + float(m["median"].predict(off)[0]))
            if shift >= best:
                factor, best = label, shift
    return {"delay_min": round(mid, 1), "range_min": (round(lo, 1), round(hi, 1)),
            "probable_factor": factor}


if __name__ == "__main__":
    example = dict(delay_start=2.0, delay_mid=2.5, prev1_delay=1.5, prev2_delay=0.5, prev3_delay=0.0,
                   hour=8, rain_flag=1, festival_flag=0)
    print("\nExample:", predict_delay(example))
