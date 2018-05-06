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
        kdj_config = kdj.get_conf(coin_id)
        trades.extend(api.get_trades(coin_id))
        #获取买入金额
        buy_usdt = kdj.get_trade_usdt('buy',coin_id,stocks,kdj_config)
        #获取卖出金额
        sell_usdt = kdj.get_trade_usdt('sell',coin_id,stocks,kdj_config)
        #获取仓位上限
        stock_limit = kdj.get_stock_limit(coin_id,stocks,kdj_config)
        #获取仓位余额
        stock_remain = kdj.get_stock_remain(coin_id,stocks,kdj_config)
        #获取当前仓位
        stock = api.get_coin_stock(coin_id,stocks)

        #取消当前未完成的挂单
        api.cancel_all_orders_by_coin_id(coin_id)
        #获取K线序列
        kline = dc_lib.get_kline(coin_id, 15,100)

        #设置KD卖出权重，剩余仓位大于0.15时为1，否则为0.7，增加卖出机会
        kdj_sell_ratio = 1 if stock_remain/stock_limit>0.17 else 0.7
        #获取KDJ序列
        kdj_data = kdj.get_kdj(coin_id,kline,sell_ratio=kdj_sell_ratio)
        #获取MA30序列
        ma30_data = dc_lib.get_mean(kline,30)

        #获取交易信号集
        signal_arr = kdj_data['kd_signal']
        #获取最新信号
        signal = signal_arr[-1]
        #获取最新收盘价
        price = kdj_data['close'][-1].item()
        #获取最新MA30
        ma30 = ma30_data[-1].item()
        #计算买卖量系数并应用
        trade_volume_factor = 1 + abs(price-ma30)*20/ma30
        buy_usdt *= trade_volume_factor
        sell_usdt *= trade_volume_factor
        
        print('coin_code:%s buy_usdt:%.2f sell_usdt:%.2f factor:%.4f sell_ratio:%.1f stock:%.2f limit:%.2f remain:%.2f '%(coin_code,round(buy_usdt,2),round(sell_usdt,2),round(trade_volume_factor,4),round(kdj_sell_ratio,1),round(stock,2),round(stock_limit,2),round(stock_remain,2)))
        
        #买入信号
        if signal == 1:
            #如果还有可用仓位则买入
            if buy_usdt and stock_remain:
                volume = max(min(buy_usdt/price,stock_remain),1.2)
                resp = api.buy(coin_id,price,volume)
                dc_lib.notify('Buy %s'%coin_code,'Price:%f Amount:%f%s'%(price,volume,get_err_msg(resp)))
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
                        resp =api.sell(coin_id,price,volume)
                        dc_lib.notify('Sell %s'%coin_code,'Price:%f Amount:%f%s'%(price,volume,get_err_msg(resp)))
            else:
                print('限制卖出')
        time.sleep(5)
    save_trades(trades)
    dc_lib.update_config({})