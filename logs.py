import datetime
import pandas as pd
from pathlib import Path
import sys 
new_trades = 1

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
if num_orders < 1:
    sys.exit("No logged stocks to sell.")
trades_to_sell = []

# find the oldest date
for i in range(new_trades):
  oldest_entry = min(buy_log, key=lambda x: x["date"])
  symbol = oldest_entry["symbol"]
  shares = oldest_entry["shares"]
  buy_log.remove(oldest_entry)
  trades_to_sell.append({
   "symbol": symbol,
   "shares": shares
})

num_orders_updated = len(buy_log)

# Convert updated buy_log back to DataFrame
df_updated = pd.DataFrame(buy_log)

# Save back to Excel
df_updated.to_excel("logged_stocks.xlsx", index=False)