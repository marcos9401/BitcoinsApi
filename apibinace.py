# -*- coding: utf-8 -*-
"""ApiBinace.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vPw-LEhrU4y4xmu4VaboCHUevFJswZuo
"""

pip install websocket-client

# Contemple a magia do IPython para garantir a compatibilidade do Python.
!wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
!tar -xzvf ta-lib-0.4.0-src.tar.gz
# %cd ta-lib
!./configure --prefix=/usr
!make
!make install
!pip install Ta-Lib
import talib
import websocket 
import talib
import numpy as np
import json

cc = 'btcusd'
interval = '1m'


socket = f'wss://stream.binance.com:9443/ws/{cc}t@kline_{interval}'

# Parâmetros de Estratégia de Negociação
aroon_time_period = 10

core_to_trade = True
core_quantity = 0

amount = 1000
core_trade_amount = amount*0.80
trade_amount = amount*0.20
money_end = amount
portfolio = 0
investment, closes, highs, lows = [], [], [], []
real_time_portfolio_value = []

# Funções de simulação de negociação de moeda


def buy(allocated_money, price):
  global money_end, portfolio, investment
  quantity = allocated_money / price
  money_end -= quantity*price
  portfolio += quantity
  if investment == []:
    investment.append(allocated_money)
  else:
    investment[-1] += investment[-2]

def sell(allocated_money,price):
  global money_end, portfolio, investment
  quantity = allocated_money / price
  money_end += quantity*price 
  portfolio -= quantity
  investment.append(-allocated_money)
  investment[-1] += investment[-2]

def on_close(ws):
  portfolio_value = portfolio*closes[-1]
  if portfolio_value > 0:
    sell(portfolio_value, price = closes[-1])
  else:
    buy(-portfolio_value, price = closes[-1])
  money_end += investment[-1]
  print('All trade settled')    

  print('close')

def on_message(ws, message):
  global closes, highs, lows, core_to_trade, core_quantity, money_end, portfolio, investment
  json_message = json.loads(message)
  cs = json_message['k']
  candle_closed, close, high, low = cs['x'], cs['c'], cs['h'], cs['l']


  if candle_closed:
    closes.append(float(close))
    highs.append(float(high))
    lows.append(float(low))
    last_price = closes[-1]
    print(f'closes: {closes}')

    if core_to_trade:
      buy(core_trade_amount, price = closes[-1])
      print(f'Core Investmente We bought$ {core_trade_amount} worth of bitcoin', '\n')
      core_quantity += core_trade_amount / closes[-1]
      core_to_trade = False
    
    aroon = talib.AROONOSC(np.array(highs), np.array(lows), aroon_time_period)
    last_aroon = round(aroon[-1],2)
    amt = last_aroon * trade_amount / 100
    port_value = portfolio*last_price - core_quantity*last_price
    trade_amt = amt - port_value
    

    RT_portfolio_value = port_value + core_quantity*last_price + money_end
    real_time_portfolio_value.append(float(RT_portfolio_value))

    print(f'The Last Aroon is"{last_aroon}" and recommended exposure is "${amt}"')
    print(f'Real-time Portfolio Value: ${RT_portfolio_value}', '\n')
    
    if trade_amt > 0:
      buy(trade_amt, price = last_price)
      print(f'We bought ${trade_amt} worth of bitcoin', '\n', '\n')
    elif trade_amt < 0:
      sell(-trade_amt, price = last_price)
      print(f'We bought ${trade_amt} worth of bitcoin', '\n', '\n')  

ws = websocket.WebSocketApp(socket, on_message=on_message, on_close = on_close)

ws.run_forever()

investment

money_end

portfolio
