import requests
import re
import pandas as pd
from datetime import date, datetime, timedelta
import time
from functions import exclude, get_data, is_date_in_range, SimpleRateLimiter, today_date, last_trading_day
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_filings_from_page(start_index=0):
    """Get filings from a specific page starting at the given index"""
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcurrent',
        'type': '4',
        'owner': 'only',
        'start': start_index,
        'count': '100'
    }
    
    headers = {
        'User-Agent': 'Personal samueltan@aptiscale.com for personal use',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }

    response = requests.get(base_url, params=params, headers=headers)
    time.sleep(0.1)  
    

    
    # Find all text file links and dates
    filing_data = re.findall(
        r'<a href="(/Archives/edgar/data/\d+/\d+/[^"]+\.txt)">\[text\]</a>.*?<td nowrap="nowrap">([\d-]+)<br>([\d:]+)</td>\s*<td nowrap="nowrap">([\d-]+)</td>',
        response.text, 
        re.DOTALL
    )
    
    page_filings = []
    accession_numbers = set()
    for i, (text_link, accepted_date, accepted_time, filing_date) in enumerate(filing_data):
      filing_date_obj = date.fromisoformat(filing_date)
      accepted_datetime = datetime.fromisoformat(f"{accepted_date}T{accepted_time}")
      
      if not is_date_in_range(filing_date_obj, filing_date1, filing_date2):
        continue 
      accession_match = re.search(r'/(\d+-\d+-\d+)\.txt', text_link)
      if accession_match:
        accession_number = accession_match.group(1)
        if accession_number in accession_numbers:  # ← CHECK FOR DUPLICATES
            continue
        accession_numbers.add(accession_number)  # ← MARK AS SEEN
    # Only process filings that pass the date filter
      text_full_url = "https://www.sec.gov" + text_link

      try:
            page_filings.append({
                'full_link': text_full_url,
                'accepted_date': accepted_date,
                'accepted_time': accepted_time,
                'filing_date': filing_date
            })
      except Exception as e:
        print(f"Error processing filing {i}: {e}")
        
        

    return page_filings 

# Your date range
filing_date1 = date(2025, 6, 1)
filing_date2 = date(2025, 11, 25)

# Collect filings from all pages
all_filings = []
start_index = 100
max_pages = 1 # Set a limit to avoid infinite loops

print("Scraping SEC filings...")

for page in range(max_pages):
    print(f"Scraping page {page + 1} (start index: {start_index})...")
    
    page_filings = get_filings_from_page(start_index)
    
    if not page_filings:
        print("No more filings found. Stopping.")
        break
    
    all_filings.extend(page_filings)
    print(f"Found {len(page_filings)} filings on this page. Total so far: {len(all_filings)}")
    
    # Check if we should continue (if we got a full page, there might be more)
    
    start_index += 100

valid_stocks = []
print(f"\nTotal filings found: {len(all_filings)}")

# Process filings to filter for Officers only
print("Processing filings to filter for Officers...")
rate_limiter = SimpleRateLimiter(max_per_sec=10)
def process_filing(filing):
    rate_limiter.wait()  # enforce 10 req/sec
    response = requests.get(filing['full_link'], headers={'User-Agent': 'Your Name your@email.com'})
    txt_content = response.text

    placeholder = get_data(txt_content)
    if placeholder[1] != "Officer" or placeholder[3] or not exclude(txt_content):  # skip non-officers and sales
        return None  # skip non-officers
    elif placeholder[4] < 1.0 and placeholder[2] > 100.0:
        valid_stocks.append(placeholder[0])
    elif placeholder[4] < 5.0 and placeholder[2] > 160000.0:
        valid_stocks.append(placeholder[0])
    filing['ticker'] = placeholder[0]
    filing['owner_type'] = placeholder[1]
    filing['amount_invested'] = placeholder[2]
    filing['excluded_all'] = int(exclude(txt_content))
    filing['stock_price'] = placeholder[4]
    return filing



filtered_filings = []

# Run 8 filings in parallel (keep under 10 req/sec)
with ThreadPoolExecutor(max_workers=9) as executor:
    futures = [executor.submit(process_filing, f) for f in all_filings]

    for future in as_completed(futures):
        result = future.result()
        if result:  # only keep Officer filings
            filtered_filings.append(result)

all_filings = filtered_filings

print(f"Final Officer filings: {len(all_filings)}")

# Create DataFrame and save to CSV
if all_filings:
    df = pd.DataFrame(all_filings)
    csv_filename = "insider_trades.csv"
    df.to_csv(r"C:\Users\samue\Downloads\insider_trades.csv", index=False)
    print(f"Data saved to {csv_filename}")
else:
    print("No Officer filings found in the specified date range.")

print(valid_stocks)