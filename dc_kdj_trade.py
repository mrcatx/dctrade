import dc_kdj_lib as kdj
import dc_api_lib as api
import dc_lib
import coins
import time
import datetime

conf_buy_usdt = 10

def get_err_msg(resp):
    if not resp['ok']:
        return '\n'+resp['msg']
    return ''

def check():
    stocks = api.get_stocks()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('check at %s'%now)
    for coin_id,coin_code in coins.g_coins.items():
        api.cancel_all_orders_by_coin_id(coin_id)
        kdj_data = kdj.get_kdj(coin_id,15,100)
        signal_arr = kdj_data['kd_signal']
        signal = signal_arr[-1]
        price = kdj_data['close'][-1].item()
        # print('%s %f'%(coin_code,price))
        # print(signal)
        if signal == 1:
            volume = conf_buy_usdt/price
            resp = api.buy(coin_id,price,volume)
            dc_lib.notify('Buy %s'%coin_code,'Price:%f Amount:%f%s'%(price,volume,get_err_msg(resp)))
        elif signal == -1:
            usable = None
            for s in stocks:
                if s['coin_id']==coin_id:
                    usable = s['usable']
            if usable != None:
                price*=0.998
                volume = min(conf_buy_usdt*2/price,usable)
                if volume * price > 1.2:
                    resp =api.sell(coin_id,price,volume)
                    dc_lib.notify('Sell %s'%coin_code,'Price:%f Amount:%f%s'%(price,volume,get_err_msg(resp)))
                    

while True:
    check()
    time.sleep(60*5)