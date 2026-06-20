"""
00 - Download and cache the SUNT dataset for offline use.

Run once before any of the forecast/visualisation scripts 03-10:
    python 00_download_data.py

Saves data/sunt.data (pickle binary) containing:
  "ts"  : DataFrame (T x 30) — hourly boardings, top 30 stops by volume
           Scripts 03-07 slice [:, :20]; scripts 08-10 use all 30 columns.
  "od"  : DataFrame          — Origin-Destination table (7 days)
  "meta": dict               — download parameters for reference
"""

import pickle
from pathlib import Path

from utils import load_od, load_timeseries

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "sunt.data"

START_DATE = "2024-04-01"
N_DAYS_TS = 60  # calendar days of boarding time series
N_DAYS_OD = 7  # calendar days of OD data
FREQ = "1h"
TOP_N = 30  # max stops needed (08/09/10); scripts 03-07 slice the first 20

DATA_DIR.mkdir(parents=True, exist_ok=True)

print(f"Downloading time series (top {TOP_N} stops, {N_DAYS_TS} days, freq={FREQ}) ...")
ts = load_timeseries(
    start_date=START_DATE,
    n_days=N_DAYS_TS,
    freq=FREQ,
    top_n=TOP_N,
)
print(f"  Shape: {ts.shape}  ({ts.index[0].date()} → {ts.index[-1].date()})")

print(f"\nDownloading OD data ({N_DAYS_OD} days) ...")
od = load_od(start_date=START_DATE, n_days=N_DAYS_OD)
print(f"  Shape: {od.shape}")

payload = {
    "ts": ts,
    "od": od,
    "meta": {
        "start_date": START_DATE,
        "n_days_ts": N_DAYS_TS,
        "n_days_od": N_DAYS_OD,
        "freq": FREQ,
        "top_n": TOP_N,
    },
}

with open(DATA_FILE, "wb") as f:
    pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

size_mb = DATA_FILE.stat().st_size / 1e6
print(f"\nSaved → {DATA_FILE.resolve()}  ({size_mb:.1f} MB)")
print("Ready. Run any script 03-10 without re-downloading.")
