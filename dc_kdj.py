# coding: utf-8

# In[491]:

import matplotlib.pylab as plt
import numpy as np
import pandas as pd

plt.rcParams['figure.figsize'] = (30, 6)
import dc_lib as dl

# In[492]:

dataset = dl.getKline('101', 15, 100)
# dataset = dataset[200:425]


# In[493]:

df = dl.convert_candle_dataframe(dataset)
df.head(3)

# In[494]:

close = df.close
high = df.high
low = df.low

# In[495]:

date = close.index.to_series()
ndate = len(date)
# date


# In[496]:

period_high = pd.Series(np.zeros(ndate - 8), index=date.index[8:])
period_low = pd.Series(np.zeros(ndate - 8), index=date.index[8:])
rsv = pd.Series(np.zeros(ndate - 8), index=date.index[8:])

# In[497]:

for j in range(8, ndate):
    period = date[j - 8:j + 1]
    i = date[j]
    period_high[i] = high[period].max()
    period_low[i] = low[period].min()
    rsv[i] = 100 * (close[i] - period_low[i]) / (period_high[i] - period_low[i])
    period_high.name = 'period_high'
    period_low.name = 'period_low'
    rsv.name = 'rsv'

# In[498]:

period_high.head(3)

# In[499]:

rsv.describe()

# In[500]:

c1_rsv = pd.DataFrame([close, rsv]).transpose()
# c1_rsv.plot(subplots=True,title='未成熟随机指标RSV')


# In[501]:

# candle.candlePlot(df)


# In[502]:

rsv1 = pd.Series([50, 50], index=date[6:8]).append(rsv)
rsv1.name = 'RSV'
rsv.head()

# In[503]:

k_value = pd.Series(0.0, index=rsv1.index)
k_value[0] = 50
for i in range(1, len(rsv1)):
    k_value[i] = 2 / 3 * k_value[i - 1] + rsv1[i] / 3

k_value.name = 'K-Value'
k_value.head()

# In[504]:

d_value = pd.Series(0.0, index=rsv1.index)
d_value[0] = 50
for i in range(1, len(rsv1)):
    d_value[i] = 2 / 3 * d_value[i - 1] + k_value[i] / 3

d_value.name = 'D-Value'
d_value.head()

# In[505]:

j_value = 3 * k_value - 2 * d_value
j_value.name = "J-Value"
j_value.head()

# In[506]:

k_signal = k_value.apply(lambda x: -1 if x > 85 else 1 if x < 20 else 0)
d_signal = d_value.apply(lambda x: -1 if x > 80 else 1 if x < 20 else 0)

kd_signal = k_signal + d_signal
kd_signal.name = 'KD-Signal'
kd_signal[kd_signal >= 1] = 1
kd_signal[kd_signal <= -1] = -1
# kd_signal[kd_signal==1]

signal = kd_signal[len(kd_signal) - 1]
with open('/Users/xun/Workspace/Source/Java/dc/target/signal.json', 'w+') as f:
    f.write('%f,%d' % (close[len(close) - 1], signal))
    f.close()

# In[507]:

kd_trade = pd.Series.copy(kd_signal)
min_close_price = min(close)
max_close_price = max(close)
kd_trade[kd_trade > 0] = max_close_price
kd_trade[kd_trade == 0] = (max_close_price - min_close_price) / 2 + min_close_price
kd_trade[kd_trade < 0] = min_close_price
# print(kd_trade[kd_trade>0])
# plt.subplot(211)
# plt.title('收盘价')
# plt.plot(close)
# plt.plot(rsv)
# plt.plot(k_value,linestyle='dashed')
# plt.plot(d_value,linestyle='-.')
# plt.plot(j_value,linestyle='--')
# plt.subplot(212)
plt.title('RSV & KD')
plt.plot(close)
# plt.plot(rsv)
# plt.plot(k_value,linestyle='dashed')
# plt.plot(d_value,linestyle='-.')
# plt.plot(j_value,linestyle='--')
plt.plot(kd_trade)
# plt.show()
