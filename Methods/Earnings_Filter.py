#companies whose annual earnings report increases every year since xxxx from tabular data

import pandas as pd
from datetime import date
start_year = input("Please enter a start year:")
keys = ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'GOOGL', 'FB', 'GOOG', 'NVDA', 'BRK-B', 'JPM', 'JNJ', 'UNH', 'HD', 'PG', 'V', 'BAC', 'MA', 'PFE', 'XOM', 'DIS', 'AVGO', 'CSCO', 'NFLX', 'TMO', 'ADBE', 'COST', 'PEP', 'ABBV', 'ACN', 'ABT', 'CVX', 'KO', 'CMCSA', 'PYPL', 'CRM', 'VZ', 'INTC', 'WFC', 'QCOM', 'LLY', 'NKE', 'WMT', 'MCD', 'MRK', 'DHR', 'T', 'LOW', 'LIN', 'TXN', 'NEE', 'INTU', 'AMD', 'UNP', 'UPS', 'PM', 'MS', 'HON', 'MDT', 'AMAT', 'ORCL', 'SCHW', 'BMY', 'RTX', 'CVS', 'GS', 'SBUX', 'C', 'BLK', 'AMGN', 'IBM', 'AMT', 'CAT', 'ISRG', 'BA', 'PLD', 'NOW', 'TGT', 'GE', 'SPGI', 'AXP', 'MU', 'ANTM', 'DE', 'COP', 'ZTS', 'MMM', 'ADP', 'BKNG', 'LRCX', 'F', 'MDLZ', 'PNC', 'ADI', 'GM', 'SYK', 'TJX', 'MO', 'GILD', 'LMT', 'CB', 'TFC', 'MMC', 'CSX', 'CCI', 'EL', 'CME', 'USB', 'SHW', 'DUK', 'CHTR', 'EW', 'MRNA', 'CI', 'ICE', 'NSC', 'SO', 'BDX', 'CL', 'FIS', 'ITW', 'EQIX', 'TMUS', 'ETN', 'KLAC', 'APD', 'FISV', 'FDX', 'COF', 'AON', 'D', 'WM', 'REGN', 'PGR', 'HCA', 'MCO', 'BSX', 'NXPI', 'NOC', 'FCX', 'ILMN', 'ADSK', 'EMR', 'ECL', 'JCI', 'VRTX', 'EOG', 'DG', 'PSA', 'EXC', 'SPG', 'TEL', 'SNPS', 'APH', 'INFO', 'XLNX', 'IQV', 'ROP', 'ATVI', 'AIG', 'IDXX', 'GD', 'MET', 'KMB', 'CDNS', 'SLB', 'MCHP', 'ORLY', 'HUM', 'APTV', 'NEM', 'DXCM', 'BK', 'CARR', 'MSCI', 'CTSH', 'TT', 'CMG', 'DLR', 'A', 'MAR', 'PXD', 'HPQ', 'AEP', 'CNC', 'GPN', 'MSI', 'DOW', 'BAX', 'AZO', 'SRE', 'MPC', 'TROW', 'SIVB', 'DD', 'PRU', 'LHX']
earnings = pd.read_excel(r"EXCEL_FILE_LOC")

earnings[['startdatetime', 'Delete']] = earnings['startdatetime'].str.split('T', expand=True)
earnings.drop('Delete', axis =1, inplace=True)
earnings['startdatetime']=pd.to_datetime(earnings['startdatetime'])

earn = earnings[earnings['startdatetime'].dt.year > int(start_year)].dropna()

def filter(df, keys):
    list=[]
    i = 0
    while i < len(keys):    
        j = earn[earn['ticker']==keys[i]]['startdatetime'].dt.year.min()
        while j < date.today().year:
            year1= [earn[(earn['startdatetime'].dt.year == int(j)) & (earn['ticker']==keys[i])]['epsactual'].sum(), keys[i], j]
            list.append(year1)
            j = j +1
        i=i+1 
    return pd.DataFrame(list, columns=['Annual Earnings', 'Stock', 'Year'])

def earnings_filter(df,keys):
    list=[]
    for j in range(len(keys)):
        if df[df['Stock']==keys[j]]['Annual Earnings'].is_monotonic_increasing:
            list.append(keys[j])
    return list
    
print(f"The companies whose annual earnings report increases every year since {start_year} are:{earnings_filter(filter(earn,keys),keys)}")
