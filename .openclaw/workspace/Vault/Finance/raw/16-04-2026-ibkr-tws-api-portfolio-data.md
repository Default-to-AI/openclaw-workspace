---
title: "TWS API: Accessing Portfolio and Account Data"
source: "https://www.interactivebrokers.com/campus/trading-lessons/python-account-portfolio/"
author: Interactive Brokers
published: 2020-08-28
created: 2026-04-16
description: "Official IBKR tutorial on using the TWS Python API to subscribe to real-time portfolio positions and account data (cash balances, P&L, margin). Covers all five account/position functions and the subscribe-and-publish update model."
tags:
  - ibkr
  - tws-api
  - python
  - portfolio-data
  - algorithmic-trading
  - account-data
---
###### Duration 10:56

###### Level Intermediate

Welcome to our lesson on retrieving real-time portfolio and account information.

Before we begin it is important to note that historical portfolio information is not available by design since TWS is a trading application. Therefore, it is not available to the API.

There are several different functions in the API which would be used to subscribe to the position updates, each follow the same subscribe and publish model where the initial subscription request is made. Then TWS will send back a complete list of all positions matching the query. Afterwards e-wrapper will continue to send back updates to the list as they occur in real time until the subscription is canceled.

The first function is **ReqAccountUpdates**.

This function causes both position and account information to be returned for a specified account. It can only be used with a single account at a time. This means it's most commonly used in single account structures. If you have a multiple account structure, such as an advisor account or a linked account, more commonly a different function will be used.

A second function which can be used to query position information is just called **ReqPositions**.

This is used to subscribe to position updates for up to 50 sub-accounts simultaneously. If you have an advisor account with multiple sub-accounts or an introducing broker account with multiple sub-accounts this would be the function commonly used.

It's important to keep in mind if there's a very large number of sub-accounts, you'd likely need to use a different function such as **ReqPositionsMulti**, which subscribes to position updates and the single sub-account and/or model portfolio.

It is commonly used in the case, where there are many sub-accounts and the function ReqPositions can't be used to receive position updates for all these accounts in real-time. Or in case you're interested in the positions in a particular model portfolio, which are sometimes enabled on request, in financial advisor or introducing broker accounts.

It's important to keep in mind that these functions will only return information about current positions in the account. They cannot return information about historical positions. If you're interested in receiving information about positions in your account from yesterday or last week, this can be obtained through flex queries or statements in Account Management. It's even possible to obtain programmatic access to flex queries using the Flexweb service.

Another common point of confusion is with cash balances.

So virtual cash positions which don't represent real cash balances but are only bookmarks used by forex traders to track trades, are returned with position information, and are represented by a Forex pair, for instance EUR.USD. However, real cash balances are returned with the account information discussed next and always listed as a single currency and not as a pair.

For instance, you might see a cash balance of $20,000 USD but if you see a pair such as EUR.USD that doesn't represent the real cash balance, but a **virtual position**. Account information such as a net liquidity in the account, cash balances and different currencies, along with the required margin amounts are returned after calling several different functions.

The first function which is commonly used, which we discussed earlier is ReqAccountUpdates.

This returns information about both positions and account data in a single account. Or in the case of financial advisor accounts, you can access aggregated data from all sub-accounts.

However, it can't be used to subscribe to updates from multiple sub-accounts simultaneously.

The second function is **reqAccountSummary**, which is more commonly used to subscribe to account updates from multiple accounts at once.

Finally, there is also the function reqAccountSummaryMulti, which is used to subscribe to account updates from a single sub-account at a time in the case where there are more than 50 sub-accounts and can also use with portfolio models.

When requesting account data from the API, a complete list of all types of data or account keys is initially returned and then updates are sent either if there is a trade or if the account value has changed within the 3-minute period. This corresponds to the same update pattern, which you can expect in the TWS account window.

Here is a short sample program using **ReqAccountUpdates**.

Notice it looks very similar to the previous programs. The only difference is the function we call here in the start function, ReqAccountUpdates, and then the callback functions we've overridden. The overridden functions handle return data or update portfolio, update account value, update account in time and account download end.

After we invoke ReqAccountUpdates for a particular account in this case, the account number can be omitted because it's connected to an active TWS session.

If you want to start a subscription, you invoke ReqAccountUpdates with true. If you want to cancel it or stop it you can call ReqAccountUpdates with false, which is what I'll do in the stop function.

After I call ReqAccountUpdates. I set the subscription to true for this account, then updates are sent first back to update account value that has different information. This can return the cash balance, the required margin for the account, or the net liquidity and so on.

Then after that data is returned, and there will be a separate callback for every key to update account value. Then we will also receive portfolio information back to the callback function update portfolio. The callback update portfolio will be one for each position in the account. You can see the different types of information returned along with the position.

See unrealized P&L, which will be the total unrealized P&L since the position was open, the realized P&L which would be the realized profit loss for the current day. If you've closed out any positions, as well as the account name, the current market value, the average cost used to open the position and of course the position size.

And then with each callback, there is some time to let the data run completely, there will be an account download end to let you know that all information has been returned.

This functionality is only called after the first full batch of information is returned and then after that you will receive updates in real-time but updated download end won't be called because there won't be a complete batch of information. It will only be those positions or those account values which have changed since the last return of data.

Since I'm already logged in the TWS, and listening on socket port 7497, I can just run this program and it should connect and then call ReqAccountUpdates, wait five seconds and the. print out all the results and then call the stop function.

**Let's take a look at the results.**

So, you can see the initial notifications returned in the error callback to let us know the market data farm is okay. Then we will receive all the different account values in alphabetical order starting with the account code, which is just the account number, it'll give us information like say accrued cash, dividend information, which is just dividends accrued in the account, the cash balances on the different currencies so you can see these are the real cash balances showing the different currencies.

For instance, my cash balance indicates that I have 0 euros, I can also see I have $271,668.68 US dollars in cash. And then we receive other information including margin information, leverage in the account, realized P&L for the account.

And then after all the account keys return, we'll receive the portfolio information.

These are the current positions in the account, so you can see for instance there's a position in Apple Inc, AAPL a position of 1000 which has a current market value of $148k and an average cost of $140.00, the total unrealized P&L is ~$7,200.00 and the realized P&L is 0.0 meaning I have not traded this position today. Then we receive a separate call back for every position in the account with that information as well as a time of when that information is current.

If we were just to leave this program, instead of calling the stop method, then make a trade in TWS, if a position was changed then we immediately received that call back to let us know there's a change in position. Though we would only see changes for that particular instrument, and we would not see changes for any other instrument.

Finally, here at the end of the first complete batch of information we received account download end just to let us know that all information has been returned. So that's our lesson for today on receiving portfolio and account information.

[TWS API Online User Guide](https://interactivebrokers.github.io/tws-api/)

[Account and Portfolio Data – API User Guide](https://interactivebrokers.github.io/tws-api/account_portfolio.html)

#### Account Updates — Python Sample

```python
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):
        self.start()

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        print("UpdatePortfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange,
              "Position:", position, "MarketPrice:", marketPrice, "MarketValue:", marketValue, "AverageCost:", averageCost,
              "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL, "AccountName:", accountName)

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", accountName)

    def updateAccountTime(self, timeStamp: str):
        print("UpdateAccountTime. Time:", timeStamp)

    def accountDownloadEnd(self, accountName: str):
        print("AccountDownloadEnd. Account:", accountName)

    def start(self):
        # Account number can be omitted when using reqAccountUpdates with single account structure
        self.reqAccountUpdates(True, "")

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()

def main():
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0)

    Timer(5, app.stop).start()
    app.run()

if __name__ == "__main__":
    main()
```
