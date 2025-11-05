import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading 
from datetime import date, datetime, timedelta
import pytz
import pandas_market_calendars as mcal

ET = pytz.timezone('US/Eastern')
nyse = mcal.get_calendar('NYSE')
def trading_day_checker(day):
  schedule = nyse.schedule(start_date=day, end_date=day)
  return not schedule.empty

now = datetime.now(ET) 


if trading_day_checker(now) == False:
    exit()
yesterday = now - timedelta(days=1)
yesterday2_date = now - timedelta(days=2)
yesterday3_date = now - timedelta(days=3)
yesterday4_date = now - timedelta(days=4)
yesterday5_date = now - timedelta(days=5)


if trading_day_checker(yesterday) == True:
    last_trading_day = yesterday
elif trading_day_checker(yesterday2_date) == True:
    last_trading_day = yesterday2_date
elif trading_day_checker(yesterday3_date) == True:
    last_trading_day = yesterday3_date
elif trading_day_checker(yesterday4_date) == True:
    last_trading_day = yesterday4_date
else:
    print("error wtf")

def is_date_in_range(check_date, start_date, end_date):

    import pytz
    ET = pytz.timezone('US/Eastern')
    
    if check_date.tzinfo is None:
        check_date = ET.localize(check_date)
    if start_date.tzinfo is None:
        start_date = ET.localize(start_date)
    if end_date.tzinfo is None:
        end_date = ET.localize(end_date)
    
    return start_date <= check_date <= end_date

print(now)
print(last_trading_day)

xml_url = "https://www.sec.gov/Archives/edgar/data/1352851/000110465925105079/tm2529988-3_4seq1.xml"
response = requests.get(xml_url, headers={'User-Agent': 'Your Company Name'})
xml_content1 = response.text

class SimpleRateLimiter:
    def __init__(self, max_per_sec):
        self.max_per_sec = max_per_sec
        self.lock = threading.Lock()
        self.timestamps = []

    def wait(self):
        with self.lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if now - t < 1]

            if len(self.timestamps) >= self.max_per_sec:
                sleep_time = 1 - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                now = time.time()
                self.timestamps = [t for t in self.timestamps if now - t < 1]

            self.timestamps.append(time.time())


def get_data(txt_content):
    # More robust patterns with whitespace handling
    ticker_matches = re.findall(r'<issuerTradingSymbol>(.*?)</issuerTradingSymbol>', txt_content)
    if not ticker_matches:
        ticker_matches = ["Unknown"]
    is_officer = len(re.findall(r'<isOfficer>\s*1\s*</isOfficer>', txt_content)) > 0
    is_director = len(re.findall(r'<isDirector>\s*1\s*</isDirector>', txt_content)) > 0
    is_10pct_owner = len(re.findall(r'<isTenPercentOwner>\s*1\s*</isTenPercentOwner>', txt_content)) > 0
    is_sale = re.search(r'<transactionCode>\s*S\s*</transactionCode>', txt_content)
    if is_officer: 
        owner_type = "Officer"
    elif is_director:
        owner_type = "Director"
    elif is_10pct_owner:
        owner_type = "10% Owner"
    else:
        owner_type = "Other"
    
    pattern = r'<transactionShares>\s*<value>(\d+)</value>\s*</transactionShares>.*?<transactionPricePerShare>\s*<value>([\d.]+)</value>'
    matches = re.findall(pattern, txt_content, re.DOTALL)
    total_investment = 0
    end_price = 0
    
    for quantity_str, price_str in matches:
        quantity = int(quantity_str)
        price = float(price_str)
        investment = quantity * price
        total_investment += investment
        end_price = price

    return [str(ticker_matches[0]), owner_type, total_investment, is_sale, end_price
    ]



def exclude(xml_content):
    return not any([
        re.search(r'<transactionCode>\s*([GIMFD])\s*</transactionCode>', xml_content),
        re.search(r'<aff10b5One>\s*1\s*</aff10b5One>', xml_content),
        re.search(r'10b5-?1|10b5\s*1|rule.10b5-?1', xml_content, re.IGNORECASE),
        re.search(r'<derivativeTable>', xml_content),
    ])

