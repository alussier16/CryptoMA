# coding: utf-8
#WILL OPEN AN HTML FILE
from datetime import datetime
import plotly.offline
import plotly.graph_objs
import numpy
import pandas
import pickle
import quandl
quandl.ApiConfig.api_key = 'zzY7_MGnNrssWChSg9LX'
plotly.offline.init_notebook_mode(connected=True)

altcoin_btc_pair = {}
exchanges = ['KRAKEN', 'COINBASE', 'BITSTAMP', 'OKCOIN', 'COINBASE']
f_exchanges = {}
alts = ['LTC', 'XMR', 'ETH', 'XEM', 'XRP', 'DASH', 'ETC']

url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'

#USING QUANDL BITCOIN API @ https://blog.quandl.com/api-for-bitcoin-data
def read_file(file_name, path):
    if(path == ''):
        path = '{}.pkl'.format(file_name).replace('/','-')
    try:
        file = pickle.load(open(path, 'rb'))
    except IOError:
        file = quandl.get(file_name, returns="pandas")
        file.to_pickle(path)
    
    print('Successfully installed {}'.format(file_name))
    return file


#PLOT DATA USING PLOTLY API @ https://plot.ly/python/
def scatter_plot(file, title, y_label='', scale='linear'):
    label_arr = list(file)
    series_arr = list(map(lambda col: file[col], label_arr))
    
    layout = plotly.graph_objs.Layout(
        title=title,
        legend=dict(orientation="h"),
        xaxis=dict(type='date'),
        yaxis=dict(
            title=y_label,
            showticklabels= not (y_label == ''),
            type=scale
        )
    )
    
    y_axis_config = dict(
        overlaying='y',
        showticklabels=False,
        type=scale )
    
    visibility = 'visible'

    trace_arr = []
    for index, series in enumerate(series_arr):
        trace = plotly.graph_objs.Scatter(
            x=series.index, 
            y=series, 
            name=label_arr[index],
            visible=visibility
        )
        
        if y_label == '':
            trace['yaxis'] = 'y{}'.format(index + 1)
            layout['yaxis{}'.format(index + 1)] = y_axis_config    
        trace_arr.append(trace)

    fig = plotly.graph_objs.Figure(data=trace_arr, layout=layout)
    plotly.offline.plot(fig, filename="view.html")


#ORGANIZE CRYPTO DATA INTO TABLE/LIST USING PANDAS
def to_table(data, label, col):
    table = {}
    for row in range(len(data)):
        table[label[row]] = data[row][col]
        
    return pandas.DataFrame(table)


#GRAB DATA FROM POLONIEX (LINK ABOVE)
def grab_data(crypto):
    file = read_file(url.format(url, '2015-01-01', datetime.now(), 86400), crypto)
    file = file.set_index('date')
    return file


for exchange in exchanges:
    f_exchanges[exchange] = read_file('BCHARTS/{}USD'.format(exchange), '')

for alt in alts:
    altcoin_btc_pair[alt] = grab_data('BTC_{}'.format(alt))

# RECALCULATE AND SMOOTH
crypto_data = to_table(list(f_exchanges.values()), list(f_exchanges.keys()), 'Weighted Price')
crypto_data.replace(0, numpy.nan, inplace=True)
crypto_data['avgprice'] = crypto_data.mean(axis=1)

for altcoin in altcoin_btc_pair.keys():
    altcoin_btc_pair[altcoin]['price'] =  altcoin_btc_pair[altcoin]['weightedAverage'] * crypto_data['avgprice']

#MERGE ALTS AND BTC INTO LIST
merged_data = to_table(list(altcoin_btc_pair.values()), list(altcoin_btc_pair.keys()), 'price')
merged_data['BTC'] = crypto_data['avgprice']

#PLOT
scatter_plot(merged_data, 'Cryptocurrency Prices (USD)',y_label='Coin Value (USD)', scale='log')

