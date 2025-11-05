from ibapi.client import *
from ibapi.wrapper import *
from tradingbot import valid_stocks
import yfinance as yf
from alpaca import get_current_price
from datetime import datetime
from pathlib import Path
import pandas as pd
from ordercounter import num_orders
import ibsync
import importlib
from ibsync import cash_balance

LOG_FILE = "logged_stocks.xlsx"

cash_left = ibsync.cash_balance
orders_left = 5 - num_orders
allocation_per_stock = cash_left / orders_left
symbols = valid_stocks
sell_orders = []
go_ahead = False

def get_current_price(symbol):
    """Get current stock price (15-20 min delayed)"""
    stock = yf.Ticker(symbol)
    return stock.info['currentPrice']

def log_execution(contract, shares):
    """Append a single buy execution to Excel"""
    new_entry = pd.DataFrame([{
        "date": datetime.today().date(),
        "symbol": contract.symbol,
        "shares": shares
    }])
    
    if Path(LOG_FILE).exists():
        existing_df = pd.read_excel(LOG_FILE)
        if existing_df.empty:
            combined_df = new_entry
        else: 
            combined_df = pd.concat([existing_df, new_entry], ignore_index=True)
    else:
        combined_df = new_entry

    combined_df.to_excel(LOG_FILE, index=False)

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.next_order_id = None
        self.pending_sells_count = 0  
        self.counter = 0



    def nextValidId(self, orderId: OrderId):
        self.next_order_id = orderId  
        

        if cash_left < 10 and len(symbols) > 0:
          from logs import trades_to_sell, num_orders_updated
          globals()['sell_orders'] = trades_to_sell
          globals()['num_orders'] = num_orders_updated
          
          self.pending_sells_count = len(trades_to_sell)
          self.counter = len(trades_to_sell)
          for trade in trades_to_sell:
            contract = Contract()
            contract.symbol = trade['symbol']
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"

            sell_order = Order()
            sell_order.orderId = self.next_order_id
            self.next_order_id += 1
            sell_order.action = "SELL"
            sell_order.orderType = "MKT"
            sell_order.totalQuantity = trade['shares']
            sell_order.tif = "DAY"

            self.placeOrder(sell_order.orderId, contract, sell_order)

        if self.pending_sells_count == 0:
            for symbol in symbols:
                  contract = Contract()
                  contract.symbol = symbol
                  contract.secType = "STK"
                  contract.exchange = "SMART"
                  contract.currency = "USD"
                  self.reqContractDetails(self.next_order_id, contract)
    def orderStatus(self,
                orderId: int,
                status: str,
                filled: float,
                remaining: float,
                avgFillPrice: float,
                permId: int,
                parentId: int,
                lastFillPrice: float,
                clientId: int,
                whyHeld: str,
                mktCapPrice: float):
            if remaining == 0:
              if go_ahead == True:
                self.counter -= 1
                if self.counter == 0:
                  importlib.reload(ibsync) 
                  globals()['go_ahead'] = False
                  from ibsync import cash_balance
                  cash_left = ibsync.cash_balance
                  orders_left = 5 - num_orders
                  allocation_per_stock1 = cash_left / orders_left
                  globals()['allocation_per_stock'] = allocation_per_stock1
                  for symbol in symbols:
                    contract = Contract()
                    contract.symbol = symbol
                    contract.secType = "STK"
                    contract.exchange = "SMART"
                    contract.currency = "USD"
                    self.reqContractDetails(self.next_order_id, contract)



    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        last_price = get_current_price(contractDetails.contract.symbol)
        shares_to_buy = int(allocation_per_stock / last_price)
        myorder = Order()
        myorder.orderId = self.next_order_id
        self.next_order_id += 1
        myorder.action = "BUY"
        myorder.tif = "DAY"
        myorder.orderType = "MKT"
        myorder.totalQuantity = shares_to_buy

        self.placeOrder(myorder.orderId, contractDetails.contract, myorder)

    def execDetails(self, reqId: int, contract: Contract, execution):
            if execution.side == "SLD":
              self.pending_sells_count -= 1
              if self.pending_sells_count == 0:
                globals()['go_ahead'] = True
            elif execution.side == "BOT":
              log_execution(contract, int(execution.cumQty))
              print(f"Logged: {contract.symbol}, {execution.shares} shares")



# Run the app
app = TestApp()
app.connect("127.0.0.1", 7497, 100)
app.run()

