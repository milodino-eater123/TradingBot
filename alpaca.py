import requests
import datetime 
API_KEY = "PKHY2HT6DV4JT7RPXVM7OTKIVU"
API_SECRET = "7yVKAaiph3grmaRWr9b8nh3JdeMJga2ESEGGbWAoD6rk"
BASE_URL = "https://data.alpaca.markets/v2"

def get_current_price(symbol):
    url = f"{BASE_URL}/stocks/{symbol}/bars?timeframe=1Day&limit=1"
    headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
    r = requests.get(url, headers=headers).json()
    bars = r.get("bars", [])
    if not bars:
        return None
    return bars[-1]["c"]

# Example
print(get_current_price("RVP"))



