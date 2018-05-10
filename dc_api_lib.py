import dc_lib as dc
import json 
import datetime
import coins

def login(ver_code):
    dc.load_config()
    data = {
        'mobile':'+86%s'%dc.get_config_value('mobile'),
        'pwd':dc.get_config_value('login_password'),
        'vercode':ver_code
    }
    print(data)
    content = dc.post('/user/login/',data)
    json_msg = json.loads(content)
    print(json_msg)
    ok = json_msg['ok']
    json_data = json_msg['data']
    if ok:
        token = json_data['token']
        uid = json_data['uid']
        dc.update_config({'token':token,'uid':uid,'login_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    return json_msg

def get_coin_stock(coin_id,stocks):
    coin_stock_list = list(filter(lambda x:x['coin_id']==coin_id,stocks))
    return coin_stock_list[0]['appraisement'] if coin_stock_list else 0
    
def get_stocks():
    url = '/my/coin/list/?ori=1'
    content = dc.get(url,unicode_escape=False)
    print(content)
    json_resp = json.loads(content)
    if json_resp['ok']:
        stocks = []
        json_data = json_resp['data']
        for v in json_data:
            stock = {
                'coin_id':str(v['coin_id']),
                'coin_code':v['code'],
                'amount':float(v['amount']),
                'usable':float(v['usable']),
                'cost':float(v['cost']),
                'price':float(v['price']),
                'appraisement':float(v['appraisement'])
            }
            if stock['amount']:
                stocks.append(stock)
        
        # print(stocks)
        return stocks
    return None

def get_orders(coin_id):
    uri = "/order/history/?symbol_id=%s&status=waiting&start=0&count=10&direction=2"%coin_id
    resp = json.loads(dc.get(uri).replace('\r\n', ''))
    # print(resp)
    if resp['ok'] and resp['data'] and resp['data']['orders']:
        orders = []
        for o in resp['data']['orders']:
            orders.append({
                'order_id':o['order_id'],
                'volume':o['volume']
            })
        return orders
    return None

def cancel_order(order_id,coin_id):
    uri = '/order/cancel/'
    data = {
        'symbol_id':coin_id,
        'order_id':order_id
    }
    resp = json.loads(dc.post(uri,data))
    ok = resp['ok']
    if not ok:
        print('cancel %s %s %s'%(order_id,ok,resp['msg']))
    return resp['ok']

def cancel_all_orders_by_coin_id(coin_id):
    orders = get_orders(coin_id)
    # print(orders)
    if not orders:
        return
    
    for order in orders:
        cancel_order(order['order_id'],coin_id)

def buy(coin_id,price,volume):
    return trade('buy',coin_id,price,volume)

def sell(coin_id,price,volume):
    return trade('sell',coin_id,price,volume)

def trade(action,coin_id,price,volume):
    trade_interval = dc.get_config_value('trade_interval')
    trades_his = get_trades(coin_id)

    if trades_his:
        last_trade = trades_his[0]
        min_diff = (datetime.datetime.now()-last_trade['time']).total_seconds()/60
        if min_diff<trade_interval:
            err_msg = '距离上次操作间隔为%d分钟，小于%d分钟'%(min_diff,trade_interval)
            log_order(action,coin_id,price,volume,False,err_msg)
            print('Trade %s error: %s'%(coin_id,err_msg))
            return {'ok':False,'msg':err_msg}
        else:
            msg = '距离上次操作间隔为%d分钟，标准为%d分钟'%(min_diff,trade_interval)
            print('Trade %s: %s'%(coin_id,msg))

    uri = '/order/%s/'%action
    data = {
        'symbol_id':coin_id,
        'price':price,
        'volume':volume,
        'trade_pwd':dc.get_config_value('trade_password')
    }
    coin_code = coins.get_code(coin_id)
    print('%s %s price=%f volume=%s'%(action,coin_code,price,volume))
    resp = json.loads(dc.post(uri,data))
    if not resp['ok']:
        print('Trade %s error: %s'%(coin_id,resp['msg']))
    log_order(action,coin_id,price,volume,resp['ok'],resp['msg'])
    return resp

def log_order(action,coin_id,price,volume,ok,msg):
    sql = 'insert into order_log(account,type,coin_id,coin_code,volume,price,err_msg ,create_time,success) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    conn = dc.get_db_conn()
    cursor = conn.cursor()
    coin_code = coins.get_code(coin_id)
    cursor.execute(sql,(dc.get_config_value('mobile'),action,coin_id,coin_code,volume,price,msg,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ok,))
    cursor.close()
    conn.commit()
    conn.close()

def get_trades(coin_id):
    uri = "/order/tradelist/?symbol_id=%s&direction=2&start=0&count=10"%coin_id
    ret = dc.get(uri)
    resp = json.loads(ret)
    trades = []
    if resp['ok'] and resp['data'] and resp['data']['trades']:
        for r in resp['data']['trades']:
            # print(r['timestamp'])
            trades.append({
                'time':datetime.datetime.fromtimestamp(int(r['timestamp'])/1000000000),
                'coin_id':r['coin_id'],
                'coin_code':coins.get_code(coin_id),
                'order_id':r['order_id'],
                'order_type':r['order_type'].lower(),
                'trade_id':r['trade_id'],
                'volume':r['volume'],
                'price':r['price'],
                'money':r['money']
            }) 
    return trades

# buy('104',1.00001,1.23123)
