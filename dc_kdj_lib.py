import dc_lib as dl
import numpy as np
import pandas as pd
import dc_api_lib as api

def get_kdj(coin_id, kline,sell_ratio = 1):
    df = dl.convert_candle_dataframe(kline)
    df.head(3)
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

    k_signal = k_value.apply(lambda x: -1 if x > 85*sell_ratio else 1 if x < 20 else 0)
    d_signal = d_value.apply(lambda x: -1 if x > 80*sell_ratio else 1 if x < 20 else 0)

    kd_signal = k_signal + d_signal
    kd_signal.name = 'KD-Signal'
    kd_signal[kd_signal >= 1] = 1
    kd_signal[kd_signal <= -1] = -1

    return {"close": close, "rsv": rsv, "k_value": k_value, "d_value": d_value, "j_value": j_value,
            "kd_signal": kd_signal}


import json

def get_conf(coin_id):
    config_set = json.load(open('/code/strategy/kdj/kdj_conf.json','r'))
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