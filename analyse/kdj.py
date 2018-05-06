import sys
import os
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append('%s/../'%cur_path)
import dc_lib
import dc_api_lib as api
import dc_kdj_lib as kdj
import coins

stocks = []
init_usdt = 1000
for coin_id,coin_code in coins.g_coins.items():
    stocks.append({
        'appraisement':init_usdt if coin_code=='USDT' else 0,
        'usable':init_usdt if coin_code=='USDT' else 0,
        'coin_id':coin_id,
        'coin_code':coin_code
    })

for coin_id,coin_code in coins.g_coins.items():
    #获取K线序列
    kline = dc_lib.get_kline(coin_id, 15,100)
    kdj_config = kdj.get_conf(coin_id)
    print(kdj_config)
    trade_action = kdj.check_trade(coin_id,stocks,kline)
    if not trade_action:
        continue
    price = trade_action[2]
    volume = trade_action[3]
    #买入信号
    if trade_action[0] == 'buy':
        #如果还有可用仓位则买入
        # resp = api.buy(coin_id,price,volume)
        dc_lib.notify('Buy %s'%coin_code,'Price:%f Amount:%f'%(price,volume))
    #卖出信号
    elif trade_action[0] == 'sell':
        # resp =api.sell(coin_id,price,volume)
        dc_lib.notify('Sell %s'%coin_code,'Price:%f Amount:%f'%(price,volume))