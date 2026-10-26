"""Convert an Open-Meteo website CSV export into data/rain_forecast_saved.csv.

Usage (from repo root): python src/import_open_meteo_csv.py <open-meteo-export.csv>

The website export is often in GMT (see utc_offset_seconds in its first lines).
This script converts the times to Indian time (IST, UTC+5:30) and snaps them to the
hour, because the track timestamps and get_context() use IST. If you can, choose
timezone "Asia/Kolkata" when you download, then the conversion does nothing.
"""
import sys
import pandas as pd

src = sys.argv[1]
dst = "data/rain_forecast_saved.csv"
IST_OFFSET = 5.5 * 3600

with open(src, encoding="utf-8") as f:
    lines = f.read().splitlines()
meta = dict(zip(lines[0].split(","), lines[1].split(",")))
file_offset = float(meta.get("utc_offset_seconds", 0))
start = next(i for i, l in enumerate(lines) if l.startswith("time,"))

df = pd.read_csv(src, skiprows=start)
precip_col = next(c for c in df.columns if c.startswith("precipitation"))
t = pd.to_datetime(df["time"]) + pd.to_timedelta(IST_OFFSET - file_offset, unit="s")
out = pd.DataFrame({"datetime": t.dt.floor("h"), "precip_mm": df[precip_col]})
out = out.drop_duplicates("datetime").sort_values("datetime")
out.to_csv(dst, index=False)
print(f"file timezone offset: {file_offset/3600:+.1f} h -> converted to IST")
print(f"saved {len(out)} hourly rows ({out.datetime.min()} to {out.datetime.max()}) to {dst}")
print(f"hours with rain >= 0.5 mm: {(out.precip_mm >= 0.5).sum()}  | max {out.precip_mm.max()} mm")
