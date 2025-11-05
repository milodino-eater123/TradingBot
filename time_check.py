import subprocess
import time
from datetime import datetime
import pytz
import sys

def run_orders():
    print("3:00 PM! Running orders.py...")
    subprocess.run([sys.executable, "orders.py"])
ET = pytz.timezone('US/Eastern')
while True:
    now = datetime.now(ET)
    
    # Check if it's 3:00 PM (15:00 in 24-hour format)
    if now.hour == 15 and now.minute == 0:
        run_orders()
        # Wait 61 seconds to prevent multiple executions
        time.sleep(700)
    else:
        print(f"Checked at {now.strftime('%H:%M:%S')} - Not 3:00 PM yet")
        time.sleep(30)  # Wait 30secs
