import requests
import re
import pandas as pd
from datetime import date
import time
from functions import exclude, get_data, is_date_in_range



def get_filings_from_page(start_index=0):
    """Get filings from a specific page starting at the given index"""
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcurrent',
        'type': '4',
        'owner': 'only',
        'start': start_index,
        'count': '40'
    }
    
    headers = {
        'User-Agent': 'Personal samueltan@aptiscale.com for personal use',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }

    response = requests.get(base_url, params=params, headers=headers)
    
    # Find all HTML format links
    html_links = re.findall(r'href="(/Archives/edgar/data/\d+/\d+/[^"]+-index\.htm)"', response.text)
    
    # Find all text file links and dates
    filing_data = re.findall(
        r'<a href="(/Archives/edgar/data/\d+/\d+/[^"]+\.txt)">\[text\]</a>.*?<td nowrap="nowrap">([\d-]+)<br>([\d:]+)</td>\s*<td nowrap="nowrap">([\d-]+)</td>',
        response.text, 
        re.DOTALL
    )
    
    page_filings = []
    for i, ((text_link, accepted_date, accepted_time, filing_date), html_link) in enumerate(zip(filing_data, html_links)):
        text_full_url = "https://www.sec.gov" + text_link
        html_full_url = "https://www.sec.gov" + html_link
        response = requests.get(html_full_url, headers={'User-Agent': 'Your Company Name your@email.com'})
        xml_link = re.findall(r'href="(/Archives/edgar/data/\d+/\d+/[^"]+\.xml)"', response.text)
        if xml_link:  # Check if xml_link is not empty
            full_link = "https://www.sec.gov" + xml_link[1] if len(xml_link) > 1 else "https://www.sec.gov" + xml_link[0]
            if is_date_in_range(date.fromisoformat(filing_date), filing_date1, filing_date2):
                page_filings.append({
                    'full_link': full_link,
                    'accepted_date': accepted_date,
                    'accepted_time': accepted_time,
                    'filing_date': filing_date
                })
        time.sleep(0.1)  # Be polite to SEC servers
    
        return page_filings

# Your date range
filing_date1 = date(2025, 6, 1)
filing_date2 = date(2025, 11, 25)

# Collect filings from all pages
all_filings = []
start_index = 0
max_pages = 2 # Set a limit to avoid infinite loops

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
    if len(page_filings) < 40:
        print("Partial page found, likely no more data. Stopping.")
        break
    
    start_index += 40
    time.sleep(1)  # Be polite between pages

print(f"\nTotal filings found: {len(all_filings)}")

# Process filings to filter for Officers only
print("Processing filings to filter for Officers...")
for i in range(len(all_filings)-1, -1, -1):
    filing = all_filings[i]
    try:
        xml = filing['full_link']
        response = requests.get(xml, headers={'User-Agent': 'Your Company Name your@email.com'})
        xml_content_1 = response.text
        placeholder = get_data(xml_content_1)
        if placeholder[1] != "Officer":
            all_filings.pop(i)
        else:
            filing['ticker'] = placeholder[0]
            filing['owner_type'] = placeholder[1]
            if exclude(xml_content_1):
              filing['excluded_all'] = int(1)
            else:
              filing['excluded_all'] = int(0)
        time.sleep(0.1)  # Be polite to SEC servers
    except Exception as e:
        print(f"Error processing filing: {e}")
        all_filings.pop(i)

print(f"Final Officer filings: {len(all_filings)}")

# Create DataFrame and save to CSV
if all_filings:
    df = pd.DataFrame(all_filings)
    csv_filename = "insider_trades.csv"
    df.to_csv(r"C:\Users\samue\Downloads\insider_trades.csv", index=False)
    print(f"Data saved to {csv_filename}")
else:
    print("No Officer filings found in the specified date range.")