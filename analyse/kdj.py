import sys
import os
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append('%s/../'%cur_path)
import dc_lib
import dc_api_lib as api
import dc_kdj_lib as kdj
import coins
import json
from collections import namedtuple

coin_set =  coins.g_coins#{ "104": "DT"}

def request_klines():
    klines = {}
    for coin_id,coin_code in coin_set.items():
        # kline = dc_lib.get_day_kline(coin_id, 1000)
        kline = dc_lib.get_kline(coin_id, 15,1000)
        klines[coin_id] = kline 
    with open('%s/data/klines.json'%cur_path,'w+') as f:
        json.dump(klines,f,indent=4)

def load_klines():
    with open('%s/data/klines.json'%cur_path,'r') as f:
        return json.load(f)

dc_lib.set_account('mock')
account_config =dc_lib.get_account_config('mock')
stocks = []
init_usdt = account_config['usdt_base']
# request_klines()
klines = load_klines()
print('Initializing')
for coin_id,coin_code in coin_set.items():
    stocks.append({
        'appraisement':0,
        'usable': 0,
        'coin_id':coin_id,
        'coin_code':coin_code
    })

usdt_stock = {
    'appraisement':init_usdt,
    'usable':init_usdt,
    'coin_id':'0',
    'coin_code':'USDT'
}
stocks.append(usdt_stock)

def update_stock(coin_id,price,volume):
    rst = list(filter(lambda x:x['coin_id']==coin_id,stocks))
    if rst:
        stock = rst[0]
        stock['usable']+=price*volume

trade_map = {}
print('Start trade')
trade_tp = namedtuple('trade',['action','price','volume','usdt'])

for coin_id,coin_code in coin_set.items():
    print('check %s'%coin_code)
    trades = []
    trade_map[coin_code] = trades
    #获取K线序列
    kline_full = klines[coin_id]
    kline_full = kline_full[:len(kline_full)]

    kdj_config = kdj.get_conf(coin_id)
    trade_config = kdj.get_trade_config(coin_id,stocks,kdj_config)
    kdj_sell_ratio = trade_config.kdj_sell_ratio
    df = dc_lib.convert_candle_dataframe(kline_full)
    ma30_data = dc_lib.get_mean(df,30)
    kdj_data_full = kdj.get_kdj(coin_id,df,sell_ratio=kdj_sell_ratio)
    kdj_data_tp = namedtuple('kdj_data',['close','rsv','k_value','d_value','j_value','kd_signal'])

    for window in range(30,len(kline_full)):
        kdj_data = kdj_data_tp(kdj_data_full.close[:window],kdj_data_full.rsv[:window],kdj_data_full.k_value[:window],kdj_data_full.d_value[:window],kdj_data_full.j_value[:window],kdj_data_full.kd_signal[:window])
        trade_action = kdj.check_trade(coin_id,stocks,df,ma30_data=ma30_data,kdj_data=kdj_data,trade_config=trade_config)
        time = df.index[:window][-1]
        if not trade_action:
            # print('Skipped %d %f %s'%(window,kdj_data.close[-1],time))
            continue
        price = trade_action.price
        volume = trade_action.volume

        #买入信号
        if trade_action.action == 'buy':
            update_stock(coin_id,price,volume)
        #卖出信号
        elif trade_action.action == 'sell':
            update_stock(coin_id,price,volume*-1)

        trades.append(trade_tp(trade_action.action,price,volume,price*volume))
        

t_buy_times = 0
t_buy_usdt = 0
t_sell_times = 0
t_sell_usdt = 0
t_profit_usdt = 0
t_usdt_remain = 0
for coin_code,trades in trade_map.items():
    buy_times = 0
    buy_usdt = 0
    sell_times = 0
    sell_usdt = 0
    profit_usdt = 0
    buy_volume = 0
    sell_volume = 0

    if not trades:
        print('trade %s not found'%coin_code)
        continue

    close_price = trades[-1].price
    
    for trade in trades:
        if trade.action == 'buy':
            buy_times+=1
            buy_usdt+=trade.usdt
            buy_volume+=trade.volume
            
            t_buy_times+=1
            t_buy_usdt+=trade.usdt
        if trade.action == 'sell':
            sell_times+=1
            sell_usdt+=trade.usdt
            sell_volume+=trade.volume

            t_sell_times+=1
            t_sell_usdt+=trade.usdt
    volume_remain = buy_volume-sell_volume
    profit_usdt = sell_usdt - buy_usdt + close_price*volume_remain
    t_profit_usdt += profit_usdt
    
    print('%s buy_times:%d sell_times:%d buy_usdt:%.2f sell_usdt:%.2f buy_volume:%.2f sell_volume:%.2f volume_remain:%.2f profit:%.2f'%(coin_code,buy_times,sell_times,round(buy_usdt,2),round(sell_usdt,2),round(buy_volume),round(sell_volume),round(volume_remain),round(profit_usdt)))
print('Total buy_times:%d sell_times:%d buy_usdt:%.2f sell_usdt:%.2f usdt_remain:%.2f profit:%.2f'%(t_buy_times,t_sell_times,round(t_buy_usdt,2),round(t_sell_usdt,2),round(t_buy_usdt-t_sell_usdt),round(t_profit_usdt)))