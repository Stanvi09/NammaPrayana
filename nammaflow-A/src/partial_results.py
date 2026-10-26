"""Partial-results pack: baselines vs model, rain/festival on-off ablation.

Usage (from repo root): python src/partial_results.py data/dummy_laps.csv
Writes results/partial_results_table.csv, results/partial_results.png,
       docs/partial_results.md (table + interpretation paragraph).

Same session-wise split as train_delay_model.py: the locked test sessions in
data/test_sessions.txt are never used here. Cross-validation is by whole session.
RE-RUN ON REAL LAPS and re-read the paragraph: its wording is chosen from the numbers.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor as GBR
from sklearn.model_selection import GroupKFold

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/dummy_laps.csv"
TARGET = "delay_majestic"
ALL = ["delay_start", "delay_mid", "prev1_delay", "prev2_delay", "prev3_delay",
       "hour", "rain_flag", "festival_flag"]
FLAGS = ["rain_flag", "festival_flag"]

df = pd.read_csv(CSV)
FEATURES = [c for c in ALL if c in df.columns]
LAST = "delay_mid" if "delay_mid" in FEATURES else "delay_start"
simulated = "dummy" in CSV or "SIMULATED" in CSV or "simulated" in CSV

test = set(pd.read_csv("data/test_sessions.txt", header=None)[0].astype(str))
dev = df[~df.session_id.astype(str).isin(test)]
if "rare_long_stop" in dev.columns:
    dev = dev[dev.rare_long_stop == 0]
dev = dev.reset_index(drop=True)
X, y, g = dev[FEATURES], dev[TARGET], dev.session_id
r = y - X[LAST]


def oof_model(cols):
    """Out-of-fold predictions, session-wise 5-fold."""
    pred = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        m = GBR(loss="absolute_error", n_estimators=200, max_depth=3,
                learning_rate=0.05, random_state=0).fit(X.iloc[tr][cols], r.iloc[tr])
        pred[te] = np.maximum(0, X.iloc[te][LAST] + m.predict(X.iloc[te][cols]))
    return pred


def score(pred):
    err = np.abs(y - pred)
    return err.mean(), (err <= 1.0).mean() * 100


rows = {
    "No delay": score(np.zeros(len(y))),
    "Same delay as now": score(X[LAST].values),
    "Same as previous train": score(X["prev1_delay"].values),
    "Model (all inputs)": score(oof_model(FEATURES)),
    "Model, rain/festival OFF": score(oof_model([c for c in FEATURES if c not in FLAGS])),
}
tab = pd.DataFrame(rows, index=["mean_abs_error_min", "pct_within_1_min"]).T.round(2)
tab.to_csv("results/partial_results_table.csv")
print(tab)

# ---- graph ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 3.8))
colors = ["#b0b0b0"] * 3 + ["#1f6fb2", "#7fb3dc"]
bars = ax.bar(tab.index, tab.mean_abs_error_min, color=colors)
ax.bar_label(bars, fmt="%.2f", padding=2)
ax.set_ylim(0, tab.mean_abs_error_min.max() * 1.18)
ax.set_ylabel("Mean absolute error (metro min)")
ax.set_title("Delay at Majestic: baselines vs model" + (" (simulated data)" if simulated else ""))
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig("results/partial_results.png", dpi=200)

# ---- interpretation paragraph (wording follows the numbers) ---------------
m, base = tab.loc["Model (all inputs)"], tab.loc["Same delay as now"]
off = tab.loc["Model, rain/festival OFF"]
best_base = tab.iloc[:3].mean_abs_error_min.min()
gain = (best_base - m.mean_abs_error_min) / best_base * 100
if m.mean_abs_error_min < best_base - 0.02:
    verdict = (f"The model beats the strongest baseline (same delay as now): its mean error is "
               f"{m.mean_abs_error_min:.2f} min against {best_base:.2f} min, a {gain:.0f}% reduction, "
               f"and {m.pct_within_1_min:.0f}% of predictions fall within 1 minute "
               f"(baseline {base.pct_within_1_min:.0f}%).")
else:
    verdict = (f"The model does not clearly beat the strongest baseline: its mean error is "
               f"{m.mean_abs_error_min:.2f} min against {best_base:.2f} min. On this data the delay "
               f"at the last checkpoint already explains most of the delay at Majestic.")
if off.mean_abs_error_min > m.mean_abs_error_min + 0.01:
    abl = (f"Switching the rain and festival flags off raises the error from "
           f"{m.mean_abs_error_min:.2f} to {off.mean_abs_error_min:.2f} min, so these context inputs help.")
else:
    abl = (f"Switching the rain and festival flags off changes the error only from "
           f"{m.mean_abs_error_min:.2f} to {off.mean_abs_error_min:.2f} min, so on this data "
           f"they add little.")
caveat = ("These numbers come from SIMULATED data, so they show that the pipeline works, not that the "
          "method works on a real metro. They must be re-run on the real testbed laps. "
          if simulated else
          "Results are from testbed laps only and say nothing yet about real Namma Metro delays. ")
para = f"{verdict} {abl} {caveat}Every result uses cross-validation split by whole session, and the locked test sessions were not used."

md = ["# Partial results: delay at Majestic", "",
      f"Data: `{CSV}` ({len(dev)} laps, {dev.session_id.nunique()} sessions, split by session).", "",
      tab.rename(columns={"mean_abs_error_min": "Mean error (min)",
                          "pct_within_1_min": "Within 1 min (%)"}).to_markdown(), "",
      "![graph](../results/partial_results.png)", "", "## Interpretation", "", para, ""]
open("docs/partial_results.md", "w").write("\n".join(md))
print("\n" + para)
