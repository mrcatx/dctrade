# from datetime import datetime
import dc_api_lib as api
import dc_lib as dc

# print(resp)

def check_stock_appraisement(account):
    dc.set_account(account)
    resp = api.get_stocks()
    appraisement = 0
    usdt = 0
    for s in resp:
        appraisement+=s['appraisement']
        if s['coin_code'] == 'USDT':
            usdt = s['usable']
    print('%s: appriasement= %.2f USDT= %.2f ratio= %.2f%%'%(account,appraisement,usdt,(appraisement-usdt)/appraisement*100))

check_stock_appraisement('18011464336')
check_stock_appraisement('18011466536')
# dc.set_account('18011464336')
# fmt = '%Y-%m-%d %H:%M:%S'
# d1 = datetime.strptime('2010-01-01 17:31:22', fmt)
# d2 = datetime.strptime('2010-01-01 17:34:22', fmt)


# t = 1525052431992320839/1000000000
# dt = datetime.fromtimestamp(t)
# now = datetime.now()
# print('diff=%d'%((now-dt).total_seconds()/60))
# print(now)
# print(dt)
# resp = api.get_trades('104')
# print(resp)
# api.buy('104',2.4370,1.2308)