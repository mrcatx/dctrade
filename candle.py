import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY, date2num
from matplotlib.finance import candlestick_ohlc

# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False


def candlePlot(seriesData, title="a"):
    Date = [date2num(date) for date in seriesData.index]
    seriesData['date'] = Date
    listData = []
    for i in range(len(seriesData)):
        a = [seriesData.date[i], seriesData.open[i], seriesData.high[i], seriesData.low[i], seriesData.close[i]]
        listData.append(a)

    ax = plt.subplot()
    mondays = WeekdayLocator(MONDAY)
    weekFormatter = DateFormatter('%y %b %d')
    # ax.xaxis.set_major_locator(mondays)
    # ax.xaxis.set_minor_locator(DayLocator())
    # ax.xaxis.set_major_formatter(weekFormatter)
    # candlestick_ohlc(ax, listData)
    candlestick_ohlc(ax, listData, width=0.007, colorup='r', colordown='g')
    ax.set_title(title)
    plt.setp(plt.gca().get_xticklabels(), rotation=50, horizontalalignment='center')
    return (plt.show())
