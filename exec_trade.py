import dc_kdj_lib as kdj
import dc_api_lib as api
import dc_lib
import coins
import time
import datetime
import sys
import math
import os
import json
cur_path = os.path.dirname(os.path.abspath(__file__))
print(cur_path)
# base_path = sys.argv[1]
account = sys.argv[1]

# dc_lib.set_base_path(base_path)
dc_lib.set_account(account)
# conf_buy_usdt = dc_lib.get_config_value('buy_usdt')
def save_stock_info(stocks):
    appraisement = 0
    usdt = 0
    for s in stocks:
        appraisement+=s['appraisement']
        if s['coin_code'] == 'USDT':
            usdt = s['usable']
    dc_lib.update_config({
        'appraisement':round(appraisement,4),
        'usdt_stock':round(usdt,4)
    })

    if stocks:
        with open('%s/data/stock_cache/%s.json'%(cur_path,account),'w+') as f:
            f.write(json.dumps(stocks,indent=4,sort_keys=True))
        f.close()
    print('%s: appriasement= %.2f USDT= %.2f ratio= %.2f%%'%(account,appraisement,usdt,(appraisement-usdt)/appraisement*100))

def save_trades(trades):
    trades = sorted(trades,key=lambda x:x['time'],reverse=True)
    for trade in trades:
        trade['time'] = trade['time'].strftime('%Y-%m-%d %H:%M:%S')

    if trades:
        with open('%s/data/trade_cache/%s.json'%(cur_path,account),'w+') as f:
            f.write(json.dumps(trades,indent=4))
        f.close()

def get_err_msg(resp):
    if not resp['ok']:
        return '\n'+resp['msg']
    return ''

stocks = api.get_stocks()
trades = []
if not stocks:
    print('账户读取错误')
else:
    save_stock_info(stocks)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('check at %s'%now)
    for coin_id,coin_code in coins.g_coins.items():
        #获取K线序列
        kline = dc_lib.get_kline(coin_id, 15,100)        
        kdj_config = kdj.get_conf(coin_id)
        trades.extend(api.get_trades(coin_id))
        df = dc_lib.convert_candle_dataframe(kline)
        trade_action = kdj.check_trade(coin_id,stocks,df)
        if not trade_action:
            continue
        price = trade_action.price
        volume = trade_action.volume
        #买入信号
        if trade_action[0] == 'buy':
            #如果还有可用仓位则买入
            resp = api.buy(coin_id,price,volume)
            dc_lib.notify('Buy %s'%coin_code,'Price:%f Amount:%f%s'%(price,volume,get_err_msg(resp)))
        #卖出信号
        elif trade_action[0] == 'sell':
            resp =api.sell(coin_id,price,volume)
            dc_lib.notify('Sell %s'%coin_code,'Price:%f Amount:%f%s'%(price,volume,get_err_msg(resp)))

        time.sleep(5)
    save_trades(trades)
    dc_lib.update_config({})