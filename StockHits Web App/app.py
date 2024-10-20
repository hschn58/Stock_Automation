import pandas as pd
import yfinance as yf
import re
from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO

app = Flask(__name__)

tickers = ['HD', 'HON', 'LMT', 'WSM', 'CLX', 'COST', 'GIS', 'MKC', 'PEP', 'BLK', 'ICE', 'JPM', 'PYPL', 'USB', 'ABT', 
           'AMGN', 'BMY', 'MRK', 'TMO', 'UNH', 'JNJ', 'WM', 'AAPL', 'AMZN', 'META', 'GOOG', 'MSFT', 'ADBE', 'ANET', 
           'CSCO', 'EBAY', 'ORCL', 'TXN', 'CNI', 'UNP', 'UPS', 'NEE', 'DUK', 'AMT', 'DLR', 'O']

def fetch_stock_data(tickers):
    data_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker).history(period='15d')
            data_list.append(stock)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    if data_list:
        DF = pd.concat(data_list, axis=1, keys=tickers)
        DF.columns.names = ['Stock Tickers', 'Stock Info']
        Closing_Price = DF.xs(key='Close', axis=1, level='Stock Info')

        Percent_Change1 = (Closing_Price / Closing_Price.shift(5) - 1) * 100
        Percent_Change2 = (Closing_Price / Closing_Price.shift(4) - 1) * 100
        Percent_Change3 = (Closing_Price / Closing_Price.shift(3) - 1) * 100

        Five_Days = Percent_Change1[Percent_Change1 < -3]
        Four_Days = Percent_Change2[Percent_Change2 < -3]
        Three_Days = Percent_Change3[Percent_Change3 < -3]

        for ticker in tickers:
            Five_Days[ticker] = Five_Days[ticker].round(3)
            Four_Days[ticker] = Four_Days[ticker].round(3)
            Three_Days[ticker] = Three_Days[ticker].round(3)

        fix_date(Five_Days)
        fix_date(Four_Days)
        fix_date(Three_Days)
    else:
        Five_Days = pd.DataFrame()
        Four_Days = pd.DataFrame()
        Three_Days = pd.DataFrame()

    return Five_Days, Four_Days, Three_Days

def fix_date(df):
    df.reset_index(inplace=True)
    df['Date'] = df['Date'].astype(str).str.split(' ').str[0]

def format_dataframe(df):
    df_copy = df.copy()
    df_copy.fillna(0, inplace=True)
    df_copy = df_copy.applymap(lambda x: int(x) if x == 0 else x)
    return df_copy

@app.route('/')
def index():
    global tickers
    Five_Days, Four_Days, Three_Days = fetch_stock_data(tickers)

    Five_Days_formatted = format_dataframe(Five_Days)
    Four_Days_formatted = format_dataframe(Four_Days)
    Three_Days_formatted = format_dataframe(Three_Days)

    five_days_html = df_to_html_table(Five_Days_formatted)
    five_days_last_html = df_to_html_table(Five_Days.iloc[-1:].dropna(axis=1))

    four_days_html = df_to_html_table(Four_Days_formatted)
    four_days_last_html = df_to_html_table(Four_Days.iloc[-1:].dropna(axis=1))

    three_days_html = df_to_html_table(Three_Days_formatted)
    three_days_last_html = df_to_html_table(Three_Days.iloc[-1:].dropna(axis=1))

    return render_template('index.html', five_days=five_days_html, five_days_last=five_days_last_html, four_days=four_days_html, four_days_last=four_days_last_html, three_days=three_days_html, three_days_last=three_days_last_html)

@app.route('/update_tickers', methods=['POST'])
def update_tickers():
    global tickers
    new_tickers = request.form['tickers'].strip().upper().split(',')
    valid_tickers = [ticker.strip() for ticker in new_tickers if re.match(r'^[A-Z0-9]+$', ticker.strip())]

    action = request.form['action']
    if valid_tickers:
        if action == 'add':
            tickers.extend([ticker for ticker in valid_tickers if ticker not in tickers])
        elif action == 'replace':
            tickers = valid_tickers

    return redirect(url_for('index'))

@app.route('/download_excel')
def download_excel():
    global tickers
    Five_Days, Four_Days, Three_Days = fetch_stock_data(tickers)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sheet_length=1

        pd.DataFrame(columns = ['Five Day Average']).to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length)
        Five_Days.to_excel(writer,index=False,header=True,sheet_name='Sheet1', startrow=sheet_length+1)

        sheet_length+=len(Five_Days)+1+1
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

        workbook = writer.book
        worksheet = workbook['Sheet1']
        worksheet.column_dimensions['A'].width = 15

    output.seek(0)

    return send_file(output, as_attachment=True, download_name='Stock_Data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def df_to_html_table(df):
    return df.to_html(classes='table table-striped', index=False)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
