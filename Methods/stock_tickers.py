import pandas as pd 
import requests 

#access data as a browser using requests.get w the header
tables = pd.read_html(requests.get('https://www.slickcharts.com/sp500', headers={'User-agent': 'Mozilla/5.0'}).text)
tableDf = tables[0]

#filter for only what's needed
data = pd.DataFrame(tableDf[0:150].drop(columns=['% Chg', 'Chg', 'Price', 'Symbol'], axis = 1))

#save
data.to_csv(PATH)
