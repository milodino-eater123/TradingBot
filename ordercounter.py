import datetime
import pandas as pd
import sys
from pathlib import Path


LOG_FILE = "logged_stocks.xlsx"
columns = ['date', 'symbol', 'shares']

# Check if file exists
if Path(LOG_FILE).exists():
    df = pd.read_excel(LOG_FILE)
    # If file is blank (no columns), create columns
    if df.empty or not all(col in df.columns for col in columns):
        df = pd.DataFrame(columns=columns)
else:
    # File missing → create it with columns
    df = pd.DataFrame(columns=columns)
    df.to_excel(LOG_FILE, index=False)

if len(df['date'].dropna()) > 0:
    df['date'] = pd.to_datetime(df['date']).dt.date

buy_log = df.to_dict(orient="records")       # convert to list of dicts

num_orders = len(buy_log)

