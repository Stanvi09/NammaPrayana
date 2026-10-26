# NammaFlow: Role A (Prediction and Decisions)

Run everything from the repo root.

```
pip install -r requirements.txt
python src/make_dummy_laps.py                 # dummy dataset -> data/dummy_laps.csv
python src/convert_raw_to_laps.py <raw.csv> <laps.csv>   # B's raw sensor log -> lap table
python src/train_delay_model.py data/dummy_laps.csv       # baselines, model, range, ablations
python src/partial_results.py data/dummy_laps.csv         # table + graph + paragraph
python src/import_open_meteo_csv.py <export.csv>          # Open-Meteo CSV -> data/rain_forecast_saved.csv (GMT -> IST)
pytest                                                    # all tests
```

| Path | What it is |
|---|---|
| `data/timetable.csv` | Track timetable (S1 Start, S3 Majestic) from B's firmware constants |
| `data/festival_calendar.csv` | Festival / match days (add match days here) |
| `data/dummy_laps.csv` | Simulated laps (labelled simulated) |
| `data/raw_train_checkpoint_data_SIMULATED.csv` | B's simulated raw log |
| `data/test_sessions.txt` | Locked test sessions. Do not evaluate on them until the final experiments |
| `src/import_open_meteo_csv.py` | Converts a downloaded Open-Meteo CSV (GMT) to IST for the saved forecast |
| `src/get_context.py` | Rain (Open-Meteo, saved-file fallback) and festival flags |
| `src/train_delay_model.py` | Baselines, model, 80% range, ablations, `predict_delay()` |
| `src/decisions.py` | Leave-Now, Connection-Saver, alternate routes |
| `src/partial_results.py` | Partial-results pack |
| `docs/problem_description.md`, `docs/partial_results.md` | Write-ups |

All results so far are on SIMULATED data. Re-run on real laps when available.
