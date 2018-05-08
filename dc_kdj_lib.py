import dc_lib as dl
import numpy as np
import pandas as pd
import dc_api_lib as api
import os
import coins
from collections import namedtuple
cur_path = os.path.dirname(os.path.abspath(__file__))

def get_kdj(coin_id, df,sell_ratio = 1):
    close = df.close
    high = df.high
    low = df.low
    date = close.index.to_series()
    ndate = len(date)
    period_high = pd.Series(np.zeros(ndate - 8), index=date.index[8:])
    period_low = pd.Series(np.zeros(ndate - 8), index=date.index[8:])
    rsv = pd.Series(np.zeros(ndate - 8), index=date.index[8:])

    for j in range(8, ndate):
        period = date[j - 8:j + 1]
        i = date[j]
        period_high[i] = high[period].max()
        period_low[i] = low[period].min()
        rsv[i] = 100 * (close[i] - period_low[i]) / (period_high[i] - period_low[i])
        period_high.name = 'period_high'
        period_low.name = 'period_low'
        rsv.name = 'rsv'

    c1_rsv = pd.DataFrame([close, rsv]).transpose()
    rsv1 = pd.Series([50, 50], index=date[6:8]).append(rsv)
    rsv1.name = 'RSV'

    k_value = pd.Series(0.0, index=rsv1.index)
    k_value[0] = 50
    for i in range(1, len(rsv1)):
        k_value[i] = 2 / 3 * k_value[i - 1] + rsv1[i] / 3

    k_value.name = 'K-Value'

    d_value = pd.Series(0.0, index=rsv1.index)
    d_value[0] = 50
    for i in range(1, len(rsv1)):
        d_value[i] = 2 / 3 * d_value[i - 1] + k_value[i] / 3

    d_value.name = 'D-Value'

    j_value = 3 * k_value - 2 * d_value
    j_value.name = "J-Value"
    j_value.head()

    k_signal = k_value.apply(lambda x: -1 if x > 80*sell_ratio else 1 if x < 20 else 0)
    d_signal = d_value.apply(lambda x: -1 if x > 80*sell_ratio else 1 if x < 20 else 0)

    kd_signal = k_signal + d_signal
    kd_signal.name = 'KD-Signal'
    kd_signal[kd_signal >= 1] = 1
    kd_signal[kd_signal <= -1] = -1

    kdj_data = namedtuple('kdj_data',['close','rsv','k_value','d_value','j_value','kd_signal'])
    return kdj_data(close,rsv,k_value,d_value,j_value,kd_signal)
    # return {"close": close, "rsv": rsv, "k_value": k_value, "d_value": d_value, "j_value": j_value,
    #         "kd_signal": kd_signal}


import json

def get_conf(coin_id):
    config_set = json.load(open('%s/strategy/kdj/kdj_conf.json'%cur_path,'r'))
    rst = list(filter(lambda x:x['coin_id']==coin_id,config_set))
    if not rst:
        return None
    return rst[0]

def get_stock_limit(coin_id,stocks,config):
    stock_ratio = config['stock_ratio']
    appraisement = 0
    for s in stocks:
        appraisement+=s['appraisement']
    stock_limit = appraisement * stock_ratio
    return stock_limit

def get_stock_remain(coin_id,stocks,config):
    stock_limit = get_stock_limit(coin_id,stocks,config)
    coin_stock = api.get_coin_stock(coin_id,stocks)
    return max(0,stock_limit-coin_stock)

def get_trade_usdt(type,coin_id,stocks,config):
    tradeable = get_tradeable(type,coin_id,config)
    if not tradeable:
        return 0
    trade_ratio = config['%s_ratio'%type]
    stock_limit = get_stock_limit(coin_id,stocks,config)
    trade_usdt = stock_limit*trade_ratio
    return trade_usdt

def get_tradeable(type,coin_id,config):
    return config.get('%s_switch'%type,False)

def get_trade_config(coin_id,stocks,kdj_config):
    #获取买入金额
    buy_usdt = get_trade_usdt('buy',coin_id,stocks,kdj_config)
    #获取卖出金额
    sell_usdt = get_trade_usdt('sell',coin_id,stocks,kdj_config)
    #获取仓位上限
    stock_limit = get_stock_limit(coin_id,stocks,kdj_config)
    #获取仓位余额
    stock_remain = get_stock_remain(coin_id,stocks,kdj_config)
    #获取当前仓位
    stock = api.get_coin_stock(coin_id,stocks)
    #设置KD卖出权重，剩余仓位大于0.15时为1，否则为0.7，增加卖出机会
    kdj_sell_ratio = 1 if stock_limit and stock_remain/stock_limit>0.17 else 0.85

    trade_config = namedtuple('config',['buy_usdt','sell_usdt','stock_limit','stock_remain','stock','kdj_sell_ratio'])
    return trade_config(buy_usdt,sell_usdt,stock_limit,stock_remain,stock,kdj_sell_ratio)
    # trade_config = {
    #     'buy_usdt':buy_usdt,
    #     'sell_usdt':sell_usdt,
    #     'stock_limit':stock_limit,
    #     'stock_remain':stock_remain,
    #     'stock':stock,
    #     'kdj_sell_ratio':kdj_sell_ratio
    # }
    # return trade_config


def check_trade(coin_id,stocks,df,ma30_data=None,kdj_data=None,trade_config=None):
    kdj_config = get_conf(coin_id)
    coin_code = coins.get_code(coin_id)

    if not trade_config:
        trade_config = get_trade_config(coin_id,stocks,kdj_config)

    if dl.account != 'mock':
        #取消当前未完成的挂单
        api.cancel_all_orders_by_coin_id(coin_id)

    buy_usdt = trade_config.buy_usdt
    sell_usdt = trade_config.sell_usdt
    stock_limit = trade_config.stock_limit
    stock_remain = trade_config.stock_remain
    stock = trade_config.stock
    kdj_sell_ratio = trade_config.kdj_sell_ratio

    # buy_usdt=float(trade_config.get('buy_usdt')),
    # sell_usdt=trade_config['sell_usdt'],
    # stock_limit=trade_config['stock_limit'],
    # stock_remain=trade_config['stock_remain'],
    # stock=trade_config['stock'],
    # kdj_sell_ratio=trade_config['kdj_sell_ratio']
    # print(type(trade_config))
    # print(trade_config)
    # print(type(buy_usdt))
    # print(buy_usdt)
    #获取KDJ序列

    if kdj_data is None:
        kdj_data = get_kdj(coin_id,df,sell_ratio=kdj_sell_ratio)

    #获取MA30序列
    if ma30_data is None:
        ma30_data = dl.get_mean(df,30)

    #获取交易信号集
    signal_arr = kdj_data.kd_signal
    #获取最新信号
    signal = signal_arr[-1]
    #获取最新收盘价
    price = kdj_data.close[-1].item()
    #获取最新MA30
    ma30 = ma30_data[-1].item()
    #计算买卖量系数并应用
    trade_volume_factor = 1 + abs(price-ma30)*20/ma30

    
    buy_usdt *= trade_volume_factor
    sell_usdt *= trade_volume_factor
    
    if dl.account != 'mock':
        print('coin_code:%s buy_usdt:%.2f sell_usdt:%.2f factor:%.4f sell_ratio:%.2f stock:%.2f limit:%.2f remain:%.2f price:%f'%(coin_code,round(buy_usdt,2),round(sell_usdt,2),round(trade_volume_factor,4),round(kdj_sell_ratio,1),round(stock,2),round(stock_limit,2),round(stock_remain,2),round(price,2)))
    
    trade = namedtuple('trade',['action','coin_id','price','volume'])
    #买入信号
    if signal == 1:
        #如果还有可用仓位则买入
        if buy_usdt and stock_remain:
            volume = min(buy_usdt/price,stock_remain)
            return trade('buy',coin_id,price,volume)
            # return('buy',coin_id,price,volume)
    #卖出信号
    elif signal == -1:
        if sell_usdt:
            usable = None
            for s in stocks:
                if s['coin_id']==coin_id:
                    usable = s['usable']
            if usable != None:
                price*=0.998
                volume = min(sell_usdt/price,usable)
                if volume * price > 1.2:
                    return trade('sell',coin_id,price,volume)
                    # return('sell',coin_id,price,volume)
    return None