"""
Helper methods to interact with OANDA's REST API
Registration needed in:
https://www.oanda.com/register/?div=7&cc=SG#/sign-up/demo

Documentation to be found here
https://developer.oanda.com/rest-live-v20/introduction/
"""
import requests
from config import API_KEY, ACCOUNT, API_SERVER

headers = {
    "Authorization": f"Bearer {API_KEY}",
    'Content-Type': 'application/json'
}


def getOpenTrades():
    """
    Will return the latest status or None if no transaction is open

    API:
    https://developer.oanda.com/rest-live-v20/trade-ep/
    curl \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <AUTHENTICATION TOKEN>" \
      "https://api-fxtrade.oanda.com/v3/accounts/<ACCOUNT>/openTrades"
    :return:
    """
    url = f'{API_SERVER}/v3/accounts/{ACCOUNT}/openTrades'
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        return result.json()


def openTrade(amount, pair='EUR_USD', stopLoss=None, takeProfit=None):
    """
    Created and sends order to broker on new trade. If limits provided it will send
    https://developer.oanda.com/rest-live-v20/order-ep/
    :param amount:
    :param pair:
    :param stopLoss:
    :param takeProfit:
    :return:
    """
    payload = {
        "order": {
            "timeInForce": "FOK",
            "instrument": pair,
            "units": amount,
            "type": 'MARKET',
            "positionFill": "DEFAULT"
        }
    }

    # add take profit
    if takeProfit:
        payload['order'].update({
            "takeProfitOnFill": {
                "timeInForce": "GTC",
                "price": str(takeProfit)
            }
        })

    # add stop loss
    if stopLoss:
        payload['order'].update({
            "stopLossOnFill": {
                "timeInForce": "GTC",
                "price": str(stopLoss)
            },
        })

    url = f'{API_SERVER}/v3/accounts/{ACCOUNT}/orders'
    result = requests.post(url, headers=headers, json=payload)
    if result.status_code == 200:
        return result.json()


def getTrades(pair='EUR_USD', state='CLOSED'):
    """
    Gets from broker list of closed trades and returns the last one
    https://developer.oanda.com/rest-live-v20/trade-ep/
    :return:
    """
    url = f'{API_SERVER}/v3/accounts/{ACCOUNT}/trades?instrument={pair}&state={state}'
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        return result.json()


def getPrice(pair='EUR_USD'):
    """
    Gets the latest price for a currency pair
    https://developer.oanda.com/rest-live-v20/pricing-ep/
    :param pair:
    :return:
    """
    url = f'{API_SERVER}/v3/accounts/{ACCOUNT}/pricing?instruments={pair}'
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        prices = result.json()
        price = prices['prices'][0]
        return price
