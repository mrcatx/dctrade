import coins
import json
import dc_kdj_lib as kdj
import dc_lib as dc
import os
import numpy as np
cur_path = os.path.dirname(os.path.abspath(__file__))
print(cur_path)
# config  = []
# for k,v in coins.g_coins.items():
#     row = {
#         'coin_id':k,
#         'coin_code':v,
#         'stock_ratio':0.1,
#         'buy_ratio':0.06,
#         'sell_ratio':0.10,
#         'buy_switch':True,
#         'sell_switch':True
#     }
#     config.append(row)

# with open('strategy/kdj/kdj_conf.json','w') as f:
#     f.write(json.dumps(config, sort_keys=True, indent=4))
#     f.close()

# c = kdj.get_conf('101')
# print(c)

kline = dc.get_kline('104',15,300)
mean = dc.get_mean(kline,30)
# print(type(mean))
j = json.loads(mean.to_json(date_format='iso'))
print(j)
with open('/Users/xun/Desktop/tmp/mean.json','w+') as f:
    json.dump(j,f,indent=4)

print(type(mean))
ma = mean[-1]
print(type(ma))
print(ma)
ma = ma.item()
print(type(ma))
print(ma)
# for r in mean:
#     print(r.index)
# print(mean)