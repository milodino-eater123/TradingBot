import requests
import pandas as pd
import yfinance as yf
from datetime import date, datetime, timedelta
import pandas_market_calendars as mcal
import sys
    # API endpoint


url = "https://www.ceowatcher.com/api/search"

    # Headers (mimic browser)
headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
nyse = mcal.get_calendar('NYSE')
def trading_day_checker(day):
  schedule = nyse.schedule(start_date=day, end_date=day)
  return not schedule.empty

today_date = date.today()
if trading_day_checker(today_date) == False:
    exit()
yesterday_date = today_date - timedelta(days=1)
yesterday2_date = today_date - timedelta(days=2)
yesterday3_date = today_date - timedelta(days=3)
yesterday4_date = today_date - timedelta(days=4)




if trading_day_checker(yesterday_date) == True:
    last_trading_day = yesterday_date
elif trading_day_checker(yesterday2_date) == True:
    last_trading_day = yesterday2_date
elif trading_day_checker(yesterday3_date) == True:
    last_trading_day = yesterday3_date
elif trading_day_checker(yesterday4_date) == True:
    last_trading_day = yesterday4_date
else:
    print("error wtf")

print(last_trading_day)



    # Optional filters: adjust as needed
print(today_date)
print(yesterday_date)
filters = {
        "insiderName": "",
        "position": {
          "officer": True,
   },
        "tradeType": "purchase",        # or "sale"
        "marketCapMax": "",
        "excludeAnomalousTransactions": True,
        "excludeEspp": True,
        "exclude10b51": True,
        "excludeTaxRelated": True,
        "excludePublicOffering": True,
        "excludeDividendReinvestment": True,
        "excludeDerivative": True,
        "filingDateFrom": "last_trading_day",
        "filingDateTo": "today_date",
        "_rsc": "k4ct0"

    }

    # Pagination parameters
page = 1
page_size = 100  # number of trades per page
max_pages = 50 # safety limit to avoid infinite loops

def get_open_price(ticker, date):
        date_formatted = datetime.fromisoformat(date).date()
        date_1 = str(date_formatted + timedelta(days=1))
        data = yf.download(ticker, start=date, end=date_1, progress=False, auto_adjust=False)
        if not data.empty:
            return data["Open"].iloc[0].item()
        


all_trades = []
valid_stocks = []
print("Fetching insider trades...")

while page <= max_pages:
        payload = {
            "filter": filters,
            "pagination": {
                "page": page,
                "pageSize": page_size
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        # Check response
        if response.status_code != 200:
            print(f"Error fetching page {page}: HTTP {response.status_code}")
            break
        
        data = response.json().get("data", [])
        
        if not data:
            print("No more data found. Finished fetching all trades.")
            break
        
        for trade in data:
            ticker = trade.get("tickerSymbol")
            filing_date = trade.get("filedAt")
            value = trade.get("transactionValue")
            price = get_open_price(ticker, filing_date)
            if price is not None:
              if price < 1.0 and float(value) >= 100.00:
                valid_stocks.append(ticker)
              elif 1.0 < price < 5.0 and float(value) >= 160000.00:
                valid_stocks.append(ticker)

            



        # Extract relevant fields
        for trade in data:
            all_trades.append({
                "Ticker": trade.get("tickerSymbol"),
                "Filed At": trade.get("filedAt"),
                "Acquired/Disposed": trade.get("acquiredDisposedCode"),
                "Transaction Value": trade.get("transactionValue"),
                    })
        
        print(f"Fetched page {page}, total trades so far: {len(all_trades)}")
        page += 1

    # Convert to DataFrame
df = pd.DataFrame(all_trades)



    # Save to CSV
csv_filename = "insider_trades.csv"
df.to_csv(r"C:\Users\samue\Downloads\insider_trades.csv", index=False)
print(f"Saved {len(df)} trades to {csv_filename}")
valid_stocks = ["RVP","RVP"]
print(valid_stocks)
