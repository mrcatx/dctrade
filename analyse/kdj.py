import sys
import os
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append('%s/../'%cur_path)
import dc_lib
import dc_api_lib as api
import dc_kdj_lib as kdj
import coins
import json

coin_set = { "104": "DT"}


def request_klines():
    klines = {}
    for coin_id,coin_code in coin_set.items():
        kline = dc_lib.get_kline(coin_id, 15,100)
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
        'appraisement':init_usdt if coin_code=='USDT' else 0,
        'usable':init_usdt if coin_code=='USDT' else 0,
        'coin_id':coin_id,
        'coin_code':coin_code
    })

print('Start trade')
for coin_id,coin_code in coin_set.items():
    #获取K线序列
    kline_full = klines[coin_id]
    for i in range(10,len(kline_full)):
        window = i+10
        print('Window %d',window)
        kline = kline_full[:window]
        # print(kline)
        kdj_config = kdj.get_conf(coin_id)
        trade_action = kdj.check_trade(coin_id,stocks,kline)
        if not trade_action:
            print('Skipped')
            continue
        price = trade_action[2]
        volume = trade_action[3]
        #买入信号
        if trade_action[0] == 'buy':
            #如果还有可用仓位则买入
            # resp = api.buy(coin_id,price,volume)
            print('Buy %s'%coin_code,'Price:%f Amount:%f'%(price,volume))
        #卖出信号
        elif trade_action[0] == 'sell':
            # resp =api.sell(coin_id,price,volume)
            print('Sell %s'%coin_code,'Price:%f Amount:%f'%(price,volume))