import json
import numpy as np
import pandas as pd
from datetime import datetime
import dc_lib
import dc_kdj_lib as kdj
import os
cur_path = os.path.dirname(os.path.abspath(__file__))
import matplotlib
from matplotlib.font_manager import FontManager, FontProperties  
klines = {}
coin_set = None

def init(_coin_set):
    global coin_set
    coin_set = _coin_set
    request_klines()
    load_klines()

def request_klines():
    for coin_id,coin_code in coin_set.items():
        kline = dc_lib.get_day_kline(coin_id, 100)
        # kline = dc_lib.get_kline(coin_id, 60,300)
        klines[coin_code] = kline 
    with open('%s/data/klines.json'%cur_path,'w+') as f:
        json.dump(klines,f,indent=4)

def load_klines():
    with open('%s/data/klines.json'%cur_path,'r') as f:
        return json.load(f)

def get_kline(coin_code):
    return klines[coin_code]
