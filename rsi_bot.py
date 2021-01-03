import websocket
import json
import pprint
import talib
import numpy
import keys
from binance.client import Client
from binance.enums import *
import pandas as pd
import time
from datetime import datetime
import os

RSI_PERIOD = 14
EMA_SIGNAL_1 = 5
EMA_SIGNAL_2 = 13
TRADE_SYMBOL = "btcusdt"
TRADE_QUANTITY = 0.001
SOCKET = "wss://stream.binance.com:9443/ws/"+TRADE_SYMBOL+"@kline_1m"
TRADE_SYMBOL = "BTCUSDT" #Capital symbols for usage with binance client
closes = []
in_position = False

client = Client(keys.apiKey, keys.secretKey)
to_csv_timestamp = datetime.today().strftime('%Y%m%d_%H%M%S')
path = os.getcwd()
filename = path + '/data/' + to_csv_timestamp + TRADE_SYMBOL+'_rsi.csv'
headings = ['timestamp','price','rsi','5EMA','13EMA']
df= pd.DataFrame([headings])
df.to_csv(filename,mode = 'a', header = None, index=False)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("send order")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position

    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    if is_candle_closed:
        closes.append(float(close))
        np_closes = numpy.array(closes)
        if len(closes) > EMA_SIGNAL_1:
            emasignal1 = talib.EMA(np_closes,timeperiod=5)
            last_ema_signal1 = emasignal1[-1]
        if len(closes) > EMA_SIGNAL_2:
            emasignal2 = talib.EMA(np_closes,timeperiod=13)
            last_ema_signal2 = emasignal2[-1]
        if len(closes) > RSI_PERIOD:
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            last_rsi = rsi[-1]
            print(f"the current rsi is {last_rsi}")
            data = [candle["t"],close,last_rsi,last_ema_signal1,last_ema_signal2]
            df = pd.DataFrame([data])
            df.to_csv(filename,mode = 'a', header = None, index=False)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
