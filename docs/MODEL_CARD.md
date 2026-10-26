# NammaFlow Crowd Prediction Model Card (Phase 15)

## Model Details
- **Developer**: Role D (Backend, Security & Crowd Engineer), NammaFlow Project.
- **Model Type**: Interpretable Multi-Threshold Decision Classifier (`InterpretableCrowdDecisionTree`).
- **Input Features**:
  1. `people_count`: Current passenger occupancy estimate in coach.
  2. `time_of_day_hour`: Hour of the day (0.0 to 24.0 float).
  3. `coach_position`: Coach index (1 through 6).
  4. `is_rush_hour`: Binary flag (1 if peak commuting hours, 0 otherwise).
  5. `stair_distance`: Distance metric from station staircase / escalator (coaches C2 and C3 are adjacent).
  6. `capacity_ratio`: Passenger count divided by nominal testbed capacity (80 persons).
- **Target Output**: 3-Class Categorical Crowd Density:
  - `"Low"` (sparse occupancy, ample seats available)
  - `"Medium"` (moderate density, limited seats)
  - `"High"` (heavy crowding, standee congestion)
- **Model Artifact**: `data/crowd_model.pkl`

---

## Intended Use
- **Primary Use**: Guiding commuters towards less congested coaches before train arrival (best coach advice).
- **Operational Scope**: Evaluated on the NammaFlow hardware testbed combining a physical IR break-beam door sensor on Coach C1 with simulated synthetic fleet telemetry on coaches C2–C6.

---

## Quantitative Evaluation & Ground-Truth Benchmarking

### Dataset
- 75 recorded crowd sessions comprising 450 coach instances.
- Ground truth verified through manual hand counting and video review across peak and off-peak sessions.
- Data split strictly by session ID (56 training sessions / 19 held-out test sessions; zero leakage between coaches of the same session).

### Results (Held-Out Test Set)
| Metric | Station-Average Baseline | NammaFlow Crowd Decision Model | Project Target | Status |
|---|---|---|---|---|
| **Overall Accuracy** | 77.19% | **93.86%** | **>= 80.00%** | **PASSED** |

### Per-Class Breakdown
| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Low** | 0.86 | 0.92 | 0.89 | 13 |
| **Medium** | 0.97 | 0.86 | 0.91 | 42 |
| **High** | 0.94 | 1.00 | 0.97 | 59 |

---

## Limitations & Scientific Boundary
1. **Hardware Testbed Context**: Evaluated on physical and simulated testbed data. We make no claim that this model directly predicts live BMRCL passenger crowds without in-situ retraining.
2. **Coach Sensor Coverage**: Only coach C1 possesses physical IR break-beam hardware. Coaches C2 through C6 are simulated deterministically using rush-hour distributions and staircase proximity models.
