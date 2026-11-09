# Delay model trained on B's simulator laps: how to plug it into the backend

Keep this layout: `src/`, `models/` and `data/` side by side.

## Install
    pip install pandas numpy scikit-learn==1.8.0 joblib requests fastapi
The saved model only loads with the same scikit-learn version (1.8.0).

## Use
Put `src/` on the Python path (or copy the .py files into the backend), then:

    from sim_service import predict_for_api_sim
    result = predict_for_api_sim({
        "timestamp": "2026-10-26T08:15:00",   # IST, ISO format
        "current_station": 3, "target_station": 8,   # 0-9 station indexes (interchanges are 1 and 8)
        "current_delay": 4.0,                 # metro minutes late right now
        "leader_delay": 2.0, "gap_to_leader": 6.0,   # train ahead (optional)
        "fault_now": 0, "recent_fault_min": 0,       # optional
        "crowd_max": 0.2, "crowd_mean": 0.15,        # optional, 0 to 1
    })

Returns JSON-ready data: `delay_min`, `range_min` [low, high], `probable_factor`
(rain / festival / none) and `context`. Add a `commuter` block (see the docstring in
`src/sim_service.py`) to also get `leave_now`, `connection` and `alternate_route`.
All times are metro minutes on one clock.

Rain and festival are filled in automatically from the timestamp. You can override them
by sending `rain_level` (0, 1, 2) and `festival` (0 or 1).

## FastAPI route
    from api_example_sim import router
    app.include_router(router)          # POST /predict

## Notes
- Trained on B's SIMULATOR data (sim_laps.csv), not real hardware laps. Say "simulated" in the paper.
- `rain_level` from the weather API uses an assumed mapping (0: under 0.5 mm/h, 1: up to 2.5, 2: above).
- `get_context` tries the live Open-Meteo API first (5 s timeout), then the saved file
  `data/rain_forecast_saved.csv`. Festival days come from `data/festival_calendar.csv`.
- When the model is retrained on real hardware laps, Role A sends a new
  `models/sim_delay_model.joblib` (or a renamed file) and the interface stays the same.
