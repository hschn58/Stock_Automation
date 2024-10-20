#creates a composition of stocks in an excel sheet from given selection and filters for price changes greater than 3% from 3 day, 4 day, and 5 day moving averages
#this is then integrated with microsoft task scheduler to be displayed at a certain time every weekday

from Methods import fix_date
import pandas as pd 
import yfinance as yf



Excel=r"Path_to_Excel.exe"
file = r"Path_to_file"

#list of stocks
key = ['HD', 'HON', 'LMT', 'WSM', 'CLX', 'COST', 'GIS', 'MKC', 'PEP', 'BLK', 'ICE', 'JPM', 'PYPL', 'USB', 'ABT', 'AMGN', 'BMY', 'MRK', 'TMO', 'UNH', 'JNJ', 'WM', 'AAPL', 'AMZN', 'META', 'GOOG', 'MSFT', 'ADBE', 'ANET', 'CSCO', 'EBAY', 'ORCL', 'TXN', 'CNI', 'UNP', 'UPS','NEE', 'DUK', 'AMT', 'DLR', 'O']

i = 0 
list = []
#grab data from yfinance
while i < len(key):
    stock=yf.Ticker(key[i]).history(period='1mo')
    list.append(stock)
    i = i + 1

DF = pd.concat(list,axis = 1, keys = key )
DF.columns.names = ['Stock Tickers','Stock Info']
Closing_Price = DF.xs(key = 'Close', axis = 1, level = 'Stock Info')
Percent_Change1 = (Closing_Price / Closing_Price.shift(5) - 1)* 100 #using shift, to go down df to get value 5 lower
Percent_Change2 = (Closing_Price / Closing_Price.shift(4) - 1)* 100
Percent_Change3 = (Closing_Price / Closing_Price.shift(3) - 1)* 100
Five_Days = Percent_Change1[Percent_Change1 < -3]    #filter for only days over the averages that results were down more than 3%
Four_Days = Percent_Change2[Percent_Change2 < -3]
Three_Days = Percent_Change3[Percent_Change3 < -3]

#Round to 3 decimal places so it looks nice
for stock in key:
    Five_Days[stock]=Five_Days[stock].round(3)
    Four_Days[stock]=Four_Days[stock].round(3)
    Three_Days[stock]=Three_Days[stock].round(3)

#Time was giving time of day as well, this gets rid of it
fix_date(Five_Days)
fix_date(Four_Days)
fix_date(Three_Days)

#remove prior file contents  

writer = pd.ExcelWriter(file, engine ='openpyxl', mode='a', if_sheet_exists='replace')
pd.DataFrame(columns = ['Five Day Average']).to_excel(writer, sheet_name='Sheet1', index = False, header = True)
writer.close()

#create new writer to append remaining contents
writer = pd.ExcelWriter(file, engine ='openpyxl', mode='a', if_sheet_exists='overlay')
sheet_length=1

Five_Days.to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length)

sheet_length+=len(Five_Days)+1
Five_Days.iloc[-1:].dropna(axis = 1).to_excel(writer,index=False,header=True, sheet_name='Sheet1', startrow=sheet_length+1)

sheet_length+=2+1
pd.DataFrame(columns = ['Four Day Average']).to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length+3)

sheet_length+=1+3
Four_Days.to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length)

sheet_length+=len(Four_Days)+1
Four_Days.iloc[-1:].dropna(axis = 1).to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length+1)

sheet_length+=2+1
pd.DataFrame(columns = ['Three Day Average']).to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length+3)

sheet_length+=1+3
Three_Days.to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length)

sheet_length+=len(Three_Days)+1
Three_Days.iloc[-1:].dropna(axis = 1).to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length+1)


writer.close()

import openpyxl as xl

work_book = xl.load_workbook(file)
sheet = work_book['Sheet1']

column = 'A'

sheet.column_dimensions[column].width = 20
work_book.save(file)
###############################
import subprocess
subprocess.run([Excel, file])
