"""
Simple system to trade FOREX using OANDA's API and implementing
Martingale's trading strategy.

Part of fun meetup.com session on Live Code Jam, in 1hr,
we met to code this and meet people.

# STEPS TO TRADE
# 1. Place a trade
# 2. if wins, place again else double down
# 3. wait until it closes and start again
# 4. visualize the earnings
# 5. deploy to Heroku

# IMPROVEMENTS
# Better than luck?
# Heuristics, e.g. if it has gone up
# Move Multiplier to a persistent state

Twitter: @juancadorado
"""
import time
from datetime import datetime
import oanda as api
import random
import firebase
from config import FIREBASE

AMOUNT = 10000
BUY = 1
SELL = -1
PIPS_TARGET = 3
CUMULATIVE_PROFITS = 0
INITIALIZED = False
MULTIPLIER = 1


def pulse():
    global CUMULATIVE_PROFITS, MULTIPLIER, INITIALIZED
    openStatus = api.getOpenTrades()
    isTransactionOpen = openStatus and len(openStatus['trades']) > 0
    if not isTransactionOpen:
        # 3. Get results of the last transaction
        last = getLastTrade()
        multiplier = getMultiplier(last)

        # 1. Determine amount of transaction based on how the last one did
        action = getAction()
        amount = action * AMOUNT * multiplier

        # 4. add stop and take profit limits
        stopLoss, takeProfit = getLimits(action)

        # 2. send order to broker with limits
        trade = api.openTrade(amount, stopLoss=stopLoss, takeProfit=takeProfit)
        MULTIPLIER = multiplier

        # 5. calculate realized profit from last transaction and add
        profit = float(last.get('realizedPL')) if INITIALIZED else 0
        INITIALIZED = True
        CUMULATIVE_PROFITS = CUMULATIVE_PROFITS + profit
        if FIREBASE:
            firebase.saveProfitSnapshot(CUMULATIVE_PROFITS, 0)
    else:
        # save to firebase and wait for the next pulse
        open = openStatus['trades'][0]
        if FIREBASE:
            firebase.saveProfitSnapshot(CUMULATIVE_PROFITS, float(open.get('unrealizedPL')))
        print(f"{datetime.now()} {open.get('instrument')}: {CUMULATIVE_PROFITS} {open.get('unrealizedPL')}")


def getMultiplier(last):
    """
    Given the last transaction determines the next multiplier using the Martingale strategy
    :return:
    """
    # get last transaction closed transaction from broker
    global MULTIPLIER
    if last:
        profit = float(last.get('realizedPL'))
        lastAmount = abs(float(last.get('initialUnits')))
        if not last or profit > 0:
            return 1
        else:
            return abs(MULTIPLIER * 2)
    else:
        return 1


def getLastTrade():
    trades = api.getTrades()
    if trades:
        trades = trades['trades']
        last = trades[0] if len(trades) > 0 else None
        return last


def getAction():
    """
    Logic to determine given prices whether we should buy, sell or none.
    Currently draws a random action, but a ML model can try to determine best action
    :return:
    """
    probability = 0.5
    select_prob = random.random()
    if select_prob < probability:
        out = BUY
    else:
        out = SELL

    print(f'Action {"BUY" if out == BUY else "SELL"}')
    return out


def getLimits(action):
    """
    Given a pair, it will pull the latest prices and determine and upper and lower limit for the prices.
    Given OANDA has fractional PIPS, we need to round as well
    :return: Tuple of two values
    """
    # get the latest price for the instrument
    price = api.getPrice()
    if price:
        ask = float(price.get('closeoutAsk'))
        bid = float(price.get('closeoutBid'))

        if action == BUY:
            stopLoss = ask - PIPS_TARGET * getPipFactor()
            takeProfit = ask + PIPS_TARGET * getPipFactor()
        else:
            stopLoss = bid + PIPS_TARGET * getPipFactor()
            takeProfit = bid - PIPS_TARGET * getPipFactor()

        return round(stopLoss, getRoundFactor()), round(takeProfit, getRoundFactor())
    else:
        return None, None


def getPipFactor(pair='EUR_USD'):
    if 'JPY' in pair:
        return 0.01
    else:
        return 0.0001


def getRoundFactor(pair='EUR_USD'):
    if 'JPY' in pair:
        return 3
    else:
        return 5


def start():
    while True:
        pulse()
        time.sleep(1)


if __name__ == "__main__":
    start()
