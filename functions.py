import re
import requests

xml_url = "https://www.sec.gov/Archives/edgar/data/1352851/000110465925105079/tm2529988-3_4seq1.xml"
response = requests.get(xml_url, headers={'User-Agent': 'Your Company Name'})
xml_content1 = response.text



def get_data(xml_content):
    ticker_matches = re.findall(r'<issuerTradingSymbol>(.*?)</issuerTradingSymbol>', xml_content)
    is_officer = len(re.findall(r'<isOfficer>1</isOfficer>', xml_content)) > 0
    is_director = len(re.findall(r'<isDirector>1</isDirector>', xml_content)) > 0
    is_10pct_owner = len(re.findall(r'<isTenPercentOwner>1</isTenPercentOwner>', xml_content)) > 0
    
    if is_officer:
        owner_type = "Officer"
    elif is_director:
        owner_type = "Director"
    elif is_10pct_owner:
        owner_type = "10% Owner"
    else:
        owner_type = "Other"
    return [str(ticker_matches[0]), owner_type
    ]

def is_date_in_range(check_date, start_date, end_date):
    return start_date <= check_date <= end_date

def exclude(xml_content):
    return not any([
        re.search(r'<transactionCode>([GIMFD])</transactionCode>', xml_content),
        re.search(r'<aff10b5One>1</aff10b5One>', xml_content),
        re.search(r'<derivativeTable>', xml_content),
        re.search(r'public offering|underwriter|secondary offering', xml_content, re.IGNORECASE),
        re.search(r'option|warrant|convertible|swap', xml_content, re.IGNORECASE)
    ])

print(exclude(xml_content1))