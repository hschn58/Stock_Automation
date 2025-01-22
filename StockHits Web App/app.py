# Import necessary libraries
import pandas as pd  # For data manipulation and analysis
import yfinance as yf  # For fetching stock data from Yahoo Finance
import re  # For regular expressions, used for validating input
from flask import Flask, render_template, request, redirect, url_for, send_file  # For building a web application
from io import BytesIO  # For handling in-memory binary streams

# Initialize the Flask application
app = Flask(__name__)

# List of stock tickers to analyze
tickers = ['HD', 'HON', 'LMT', 'WSM', 'CLX', 'COST', 'GIS', 'MKC', 'PEP', 'BLK', 'ICE', 'JPM', 'PYPL', 'USB', 'ABT', 
           'AMGN', 'BMY', 'MRK', 'TMO', 'UNH', 'JNJ', 'WM', 'AAPL', 'AMZN', 'META', 'GOOG', 'MSFT', 'ADBE', 'ANET', 
           'CSCO', 'EBAY', 'ORCL', 'TXN', 'CNI', 'UNP', 'UPS', 'NEE', 'DUK', 'AMT', 'DLR', 'O']

# Function to fetch stock data for the given tickers
def fetch_stock_data(tickers):
    data_list = []  # To store stock data for each ticker
    for ticker in tickers:
        try:
            # Fetch historical data for the past 15 days
            stock = yf.Ticker(ticker).history(period='15d')
            data_list.append(stock)
        except Exception as e:
            # Handle any errors during data fetching
            print(f"Error fetching data for {ticker}: {e}")
    if data_list:
        # Combine all stock data into a single DataFrame
        DF = pd.concat(data_list, axis=1, keys=tickers)
        DF.columns.names = ['Stock Tickers', 'Stock Info']  # Label columns
        Closing_Price = DF.xs(key='Close', axis=1, level='Stock Info')  # Extract closing prices

        # Calculate percentage changes for the last 3-5 days
        Percent_Change1 = (Closing_Price / Closing_Price.shift(5) - 1) * 100
        Percent_Change2 = (Closing_Price / Closing_Price.shift(4) - 1) * 100
        Percent_Change3 = (Closing_Price / Closing_Price.shift(3) - 1) * 100

        # Filter stocks with a percentage drop greater than 3% for each period
        Five_Days = Percent_Change1[Percent_Change1 < -3]
        Four_Days = Percent_Change2[Percent_Change2 < -3]
        Three_Days = Percent_Change3[Percent_Change3 < -3]

        # Round values to 3 decimal places for readability
        for ticker in tickers:
            Five_Days[ticker] = Five_Days[ticker].round(3)
            Four_Days[ticker] = Four_Days[ticker].round(3)
            Three_Days[ticker] = Three_Days[ticker].round(3)

        # Format the date in the DataFrames
        fix_date(Five_Days)
        fix_date(Four_Days)
        fix_date(Three_Days)
    else:
        # Return empty DataFrames if no data is available
        Five_Days = pd.DataFrame()
        Four_Days = pd.DataFrame()
        Three_Days = pd.DataFrame()

    return Five_Days, Four_Days, Three_Days

# Function to format the date column in a DataFrame
def fix_date(df):
    df.reset_index(inplace=True)  # Reset the index to make the date a column
    df['Date'] = df['Date'].astype(str).str.split(' ').str[0]  # Keep only the date part

# Function to format a DataFrame for HTML display
def format_dataframe(df):
    df_copy = df.copy()  # Create a copy of the DataFrame
    df_copy.fillna(0, inplace=True)  # Replace NaN values with 0
    df_copy = df_copy.applymap(lambda x: int(x) if x == 0 else x)  # Convert 0 to integer for consistency
    return df_copy

# Route for the homepage
@app.route('/')
def index():
    global tickers
    # Fetch stock data for all tickers
    Five_Days, Four_Days, Three_Days = fetch_stock_data(tickers)

    # Format the DataFrames for display
    Five_Days_formatted = format_dataframe(Five_Days)
    Four_Days_formatted = format_dataframe(Four_Days)
    Three_Days_formatted = format_dataframe(Three_Days)

    # Convert DataFrames to HTML tables
    five_days_html = df_to_html_table(Five_Days_formatted)
    five_days_last_html = df_to_html_table(Five_Days.iloc[-1:].dropna(axis=1))

    four_days_html = df_to_html_table(Four_Days_formatted)
    four_days_last_html = df_to_html_table(Four_Days.iloc[-1:].dropna(axis=1))

    three_days_html = df_to_html_table(Three_Days_formatted)
    three_days_last_html = df_to_html_table(Three_Days.iloc[-1:].dropna(axis=1))

    # Render the index template with the data
    return render_template('index.html', five_days=five_days_html, five_days_last=five_days_last_html, 
                           four_days=four_days_html, four_days_last=four_days_last_html, 
                           three_days=three_days_html, three_days_last=three_days_last_html)

# Route for updating the tickers list
@app.route('/update_tickers', methods=['POST'])
def update_tickers():
    global tickers
    # Parse and validate the new tickers
    new_tickers = request.form['tickers'].strip().upper().split(',')
    valid_tickers = [ticker.strip() for ticker in new_tickers if re.match(r'^[A-Z0-9]+$', ticker.strip())]

    # Add or replace tickers based on user action
    action = request.form['action']
    if valid_tickers:
        if action == 'add':
            tickers.extend([ticker for ticker in valid_tickers if ticker not in tickers])
        elif action == 'replace':
            tickers = valid_tickers

    return redirect(url_for('index'))

# Route for downloading stock data as an Excel file
@app.route('/download_excel')
def download_excel():
    global tickers
    # Fetch stock data for all tickers
    Five_Days, Four_Days, Three_Days = fetch_stock_data(tickers)

    # Create an in-memory Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write data for different periods to the Excel file
        pd.DataFrame(columns=['Five Day Average']).to_excel(writer, index=False, header=True, sheet_name='Sheet1', startrow=1)
        Five_Days.to_excel(writer, index=False, header=True, sheet_name='Sheet1', startrow=2)
        pd.DataFrame(columns=['Four Day Average']).to_excel(writer, index=False, header=True, sheet_name='Sheet1', startrow=20)
        Four_Days.to_excel(writer, index=False, header=True, sheet_name='Sheet1', startrow=21)
        pd.DataFrame(columns=['Three Day Average']).to_excel(writer, index=False, header=True, sheet_name='Sheet1', startrow=40)
        Three_Days.to_excel(writer, index=False, header=True, sheet_name='Sheet1', startrow=41)

    # Reset the stream position to the beginning
    output.seek(0)

    # Send the file as a downloadable response
    return send_file(output, as_attachment=True, download_name='Stock_Data.xlsx', 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Function to convert a DataFrame to an HTML table
def df_to_html_table(df):
    return df.to_html(classes='table table-striped', index=False)

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5001)
