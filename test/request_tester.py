from config import *
from stocks.poloniex import poloniex_api as stock
from time import time
from pprint import pprint


pol = stock.Poloniex(conf_api_key, conf_api_secret)

to = int(time())
fr = to - conf_public_trades_limit * 24 * 3600
lim = 10000

res = pol.returnTradeHistory(currencyPair='USDT_BTC', start=fr, end=to, limit=lim)
pprint(res)
