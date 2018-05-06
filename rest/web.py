import sys
sys.path.append('/code/')
sys.path.append('/Users/xun/Workspace/Source/python/dctrade/')
import dc_lib
import dc_api_lib as api
from flask import Flask, render_template, request, redirect
import time
import logging
logging.basicConfig(level=logging.DEBUG)
import os
import json
from operator import itemgetter, attrgetter
from datetime import datetime

cur_path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
accounts = ['18011464336','18011466536']

@app.route('/')
def index():
    data = []
    appraisement_usdt_total = 0
    base_usdt_total = 0
    for account in accounts:
        config = dc_lib.get_account_config(account)
        appraisement = round(config.get('appraisement',-1),2)
        usdt = config.get('usdt_stock',-1)
        usdt_base = config.get('usdt_base',-1)
        ratio = round((appraisement-usdt)/appraisement*100,2)
        floats = round(appraisement-usdt_base,2)
        profit_ratio = round(floats/usdt_base*100,2)

        appraisement_usdt_total += appraisement
        base_usdt_total += usdt_base
        data.append({
            'account':account,
            'appraisement_usdt':appraisement,
            'appraisement_rmb':round(appraisement*6.5,0),
            'usdt_stock':usdt,
            'ratio':ratio,
            'floats':floats,
            'profit_ratio':profit_ratio,
            'profit_color':'red' if floats>0 else 'green',
            'login_time':config.get('login_time','-'),
            'update_time':config.get('update_time','-')
        })
    profit_usdt = appraisement_usdt_total-base_usdt_total
    summary = {
        'profit_color':'red' if profit_usdt>0 else 'green',
        "profit_rmb": round(profit_usdt*6.5,2),
        "profit_ratio": round(profit_usdt/base_usdt_total*100,2)
    }
    return render_template('index.html', accounts=data, summary=summary)

@app.route('/login_form')
def login_form():
    account = request.args.get('account')
    config = dc_lib.get_account_config(account)
    data = {
        'src':'%s/user/img_vercode/send/?usage=login&hwid=%s&time=%f'%(dc_lib.dc_base_url,config['hwid'],time.time()),
        'account':account
    }
    return render_template('login_form.html', vercode=data)

@app.route('/do_login', methods = ['POST'])
def do_login():
    account = request.form['account']
    vercode = request.form['vercode']
    dc_lib.set_account(account)
    resp = api.login(vercode)
    return render_template('resp.html',resp=resp,ret='/',action='Login for %s with %s'%(account,vercode))

@app.route('/stock_list')
def stock_list():
    account = request.args.get('account')
    stock_data = []
    with open('%s/../data/stock_cache/%s.json'%(cur_path,account),'r') as f:
        stock_data = json.load(f)
        f.close()

    appraisement = 0
    for stock in stock_data:
        appraisement += stock['appraisement']

    for stock in stock_data:
        stock['appraisement'] = round(stock['appraisement'],2)
        stock['ratio'] = round(stock['appraisement']/appraisement*100,2)

    stock_data = sorted(stock_data,key=lambda k:0 if k['coin_code']=='USDT' else k['appraisement'],reverse=True)

    return render_template('stock_list.html',stock_data=stock_data,appraisement=appraisement)

@app.route('/trade_list')
def trade_list():
    account = request.args.get('account')
    coin_code = request.args.get('coin_code')
    trade_data = []
    with open('%s/../data/trade_cache/%s.json'%(cur_path,account),'r') as f:
        trade_data = json.load(f)
        if coin_code:
            trade_data = list(filter(lambda x:x['coin_code']==coin_code,trade_data))
        f.close()

    # for trade in trade_data:
        
        # stock['ratio'] = round(stock['appraisement']/appraisement*100,2)

    return render_template('trade_list.html',trade_data=trade_data,account=account,coin_code=coin_code)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)