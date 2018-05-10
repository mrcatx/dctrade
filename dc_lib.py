import json

import pandas as pd
import requests
import pymysql
import datetime
import os
import sys
cur_path = os.path.dirname(os.path.abspath(__file__))

db_host = '39.105.18.24'
db_user = 'root'
db_pwd = 'colorful2018'
db_db = 'dc_kdj'

dc_base_url = 'https://a.dragonex.im'
status_config = {}

base_path = '%s/'%cur_path
conf_dir = 'data/'
# conf_dir = '/Users/xun/Workspace/Source/python/dc/data'
# conf_file = '%s/18011464336.json'%conf_dir
dt_format = '%Y-%m-%d %H:%M:%S'

account = None

# def set_base_path(base_path):
#     global conf_dir
    # conf_dir = '%s%s'%(base_path,conf_dir)

def set_account(_account):
    global account
    global status_config
    account = _account
    status_config = {}

def get_conf_file_path():
    return '%s%s%s.json'%(base_path,conf_dir,account)

def update_config(data):
    status_config.update(data)
    now = datetime.datetime.now()
    now_str = now.strftime(dt_format)
    status_config['update_time'] = now_str
    with open(get_conf_file_path(), 'w') as f:
        json.dump(status_config, f, sort_keys=True, indent=4)
        f.close()
    

def get_db_conn():
    return pymysql.connect(user=db_user, password=db_pwd, host=db_host, database=db_db, charset='utf8')

def get_request_headers():
    load_config()
    return {
            'hwid':get_config_value('hwid'),
            'os':'web',
            'token':get_config_value('token'),
            'Referer':'https://dragonex.im/',
            'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }

def post(uri,data):
    url = dc_base_url+uri
    headers = get_request_headers()
    r = requests.post(url,data=data,headers=headers).content.decode('unicode_escape')
    return r.replace('\r\n', '')

def get(uri,unicode_escape=True):
    url = dc_base_url+uri
    headers = get_request_headers()
    r = requests.get(url,headers=headers).content
    if unicode_escape:
        r = r.decode('unicode_escape')
    return r.replace('\r\n', '')


def load_config():
    conf_file = get_conf_file_path()
    global status_config
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    if os.path.exists(conf_file):
        with open(conf_file, 'r') as f:
            status_config.update(json.load(f))
    else:
        print('config[%s] not found',conf_file)
        status_config = {}

def get_day_kline(coinId,count):
    http_host = "https://a.dragonex.im"
    url = '%s/market/kline/?coin_id=%s&direction=2&cycle=1day&callback=_jsonpeu8l43oe2lp&count=%d' % (
        http_host, coinId, count)
    r = str(requests.get(url).content, 'utf8')
    idx_l = r.find("(")
    idxR = r.find(")")
    r = r[idx_l + 1:idxR]
    j = json.loads(r)['data']
    return j

def get_kline(coinId, minutes, count):
    http_host = "https://a.dragonex.im"
    url = '%s/market/kline/?coin_id=%s&direction=2&cycle=%dmin&callback=_jsonpeu8l43oe2lp&count=%d' % (
        http_host, coinId, minutes, count)
    r = str(requests.get(url).content, 'utf8')
    idx_l = r.find("(")
    idxR = r.find(")")
    r = r[idx_l + 1:idxR]
    j = json.loads(r)['data']
    return j

def get_mean(df,window):
    mean = df.close.rolling(window=window,center=False).mean()
    return mean

def get_account_config(account):
    conf_file = '%s%s%s.json'%(base_path,conf_dir,account)
    with open(conf_file, 'r') as f:
        return json.load(f)
    return {}

def update_account_config(account,data):
    conf_file = '%s%s%s.json'%(base_path,conf_dir,account)
    status_config.update(data)
    now = datetime.datetime.now()
    now_str = now.strftime(dt_format)
    status_config['update_time'] = now_str
    with open(conf_file, 'w') as f:
        json.dump(status_config, f)
        f.close()

def get_config_value(code):
    if not status_config:
        load_config()
    # print(status_config)
    # print('%s=%s'%(code,status_config.get(code,None)))
    return status_config.get(code,None)

def convert_candle_dataframe(dataset):
    df = pd.DataFrame(dataset)
    df.timestamp = df.timestamp.astype(int) * 1000000000
    date = pd.to_datetime(df.timestamp)
    df.index = date
    df['open'] = df.open_price.astype(float)
    df['close'] = df.close_price.astype(float)
    df['high'] = df.max_price.astype(float)
    df['low'] = df.min_price.astype(float)

    df = df.drop('timestamp', 1)
    df = df.drop('open_price', 1)
    df = df.drop('close_price', 1)
    df = df.drop('max_price', 1)
    df = df.drop('min_price', 1)
    return df


def notify(title, text):
    print(text)
    # if title:
    #     os.system("""
    #           osascript -e 'display notification "{}" with title "{}"'
    #           """.format(text, title))
    # else:
    #     os.system("""
    #           osascript -e 'display notification "{}"'
    #           """.format(text))

def simple_notify(text):
    notify(None,text)
              