# Problem description: what we predict and from which inputs (Role A)

**Question.** The train is X minutes late at the last checkpoint it has passed. How late will it be at Majestic, the interchange, and what should the commuter do about it?

**Prediction target.** `delay_majestic`: actual minus scheduled arrival time at Majestic, in metro minutes (testbed seconds converted with the agreed time scale, currently 1 s = 5 s metro time). Early arrival counts as 0.

**Output.** A median delay, an 80% range (10th to 90th percentile, e.g. 6 to 9 min), and a probable contributing factor: rain, festival / match day, or none. We never claim a cause.

**Inputs (known before the train reaches Majestic)**

| Input | Meaning |
|---|---|
| `delay_start` (and `delay_mid` if the track has a Mid sensor) | Delay at the checkpoints already passed |
| `prev1_delay`, `prev2_delay`, `prev3_delay` | Majestic delay of the last three trains in the same session (delay propagation, as in Ding et al. 2021) |
| `hour` | Hour of day |
| `rain_flag` | Rain yes/no from Open-Meteo (`get_context`) |
| `festival_flag` | Festival or match day yes/no from `data/festival_calendar.csv` |

**Method.** The model predicts the increase over the last checkpoint's delay (gradient boosting), so it starts from the strongest simple baseline and learns only what is added. Quantile models (10th and 90th percentile) give the range.

**Baselines.** (1) no delay, (2) same delay as now, (3) same delay as the previous train.

**Evaluation rules.** Split by whole session, never by lap. A test set of whole sessions (`data/test_sessions.txt`) is locked until the final experiments. Rare long stops are kept out of training for the "unseen delay types" test. Metrics: mean absolute error, share of predictions within 1 minute, and whether the 80% range really covers about 80% of cases.

**Decisions built on the prediction** (`src/decisions.py`): Leave-Now, Connection-Saver (alerts only when the median prediction misses the connection), and alternate routes when the delay is over 5 minutes.

**Limits.** Trained on a model-train testbed, not real Namma Metro data. Rain and festival are context flags, not proven causes.
