from ib_insync import IB

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

summary = ib.accountSummary()

# filter for AvailableFunds in SGD (adjust currency)
cash_balance = None
for av in summary:
    if av.tag == 'CashBalance' and av.currency == 'SGD':
        cash_balance = float(av.value)
        break

print("Available cash:", cash_balance)

ib.disconnect()

