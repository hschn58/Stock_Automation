import pandas as pd
import yahoo_fin.stock_info as si
import datetime

histfile = pd.read_excel(r'HISTORY_LOC')
divfile = pd.read_excel(r'DIVIDENDS_LOC')

histcolumns = histfile.columns 
divcolumns = divfile.columns 

keys = ['AAPL', 'MSFT', 'AMZN', 'BRK.B', 'GOOGL', 'JNJ', 'GOOG', 'UNH', 'XOM', 'JPM', 'PG', 'NVDA', 'V', 'HD', 'CVX', 'MA', 'TSLA', 'ABBV', 'MRK', 'META', 'LLY', 'PFE', 'PEP', 'KO', 'BAC', 'AVGO', 'TMO', 'WMT', 'COST', 'ABT', 'CSCO', 'MCD', 'VZ', 'DIS', 'DHR', 'ACN', 'NEE', 'WFC', 'CMCSA', 'PM', 'ADBE', 'BMY', 'TXN', 'NKE', 'LIN', 'RTX', 'COP', 'AMGN', 'NFLX', 'HON', 'T', 'CRM', 'ORCL', 'IBM', 'UPS', 'SCHW', 'CAT', 'UNP', 'LOW', 'QCOM', 'SBUX', 'CVS', 'GS', 'BA', 'DE', 'INTC', 'MS', 'ELV', 'SPGI', 'LMT', 'GILD', 'MDT', 'INTU', 'BLK', 'PLD', 'AMD', 'AMT', 'ADP', 'ISRG', 'TJX', 'CB', 'CI', 'C', 'MDLZ', 'AXP', 'PYPL', 'TMUS', 'AMAT', 'SYK', 'BKNG', 'ADI', 'MMC', 'MO', 'DUK', 'GE', 'REGN', 'PGR', 'SO', 'NOC', 'SLB', 'VRTX', 'NOW', 'EOG', 'BDX', 'TGT', 'MMM', 'ZTS', 'APD', 'BSX', 'CL', 'CSX', 'PNC', 'FISV', 'ETN', 'AON', 'HUM', 'USB', 'ITW', 'EQIX', 'CME', 'CCI', 'EL', 'MU', 'TFC', 'WM', 'MRNA', 'NSC', 'ICE', 'LRCX', 'FCX', 'EMR', 'DG', 'GD', 'ATVI', 'MPC', 'PXD', 'HCA', 'MCK', 'SHW', 'KLAC', 'ORLY', 'D', 'GIS', 'GM', 'PSX', 'VLO', 'MET', 'F', 'AEP', 'SRE', 'SNPS', 'AIG', 'EW', 'ADM', 'ROP', 'AZO', 'APH', 'KMB', 'OXY', 'A', 'JCI', 'TRV', 'CNC', 'DXCM', 'MCO', 'FDX', 'CDNS', 'PSA', 'MSI', 'EXC', 'CTVA', 'ROST', 'AFL', 'FIS', 'NEM', 'NXPI', 'MAR', 'TT', 'O', 'ADSK', 'LHX', 'DVN', 'BIIB', 'AJG', 'WMB', 'CHTR', 'HES', 'SYY', 'MNST', 'IQV', 'SPG', 'PH', 'MCHP', 'XEL', 'DOW', 'CMG', 'ALL', 'CTAS', 'TEL', 'MSCI', 'PRU', 'PAYX', 'YUM', 'KMI', 'COF', 'NUE', 'ECL', 'DD', 'HAL', 'CARR', 'IDXX', 'HLT', 'BK', 'PCAR', 'STZ', 'ED', 'OTIS', 'MTD', 'AMP', 'CMI', 'EA', 'KHC', 'TDG', 'HSY', 'ENPH', 'WELL', 'ILMN', 'AME', 'FTNT', 'PEG', 'CSGP', 'KEYS', 'SBAC', 'VICI', 'RMD', 'DLTR', 'KDP', 'CTSH', 'ROK', 'KR', 'WEC', 'DHI', 'BKR', 'OKE', 'ES', 'STT', 'PPG', 'GPN', 'AWK', 'DLR', 'VRSK', 'IFF', 'DFS', 'WTW', 'CEG', 'ANET', 'ZBH', 'ABC', 'BAX', 'FAST', 'APTV', 'GLW', 'CPRT', 'ON', 'ODFL', 'RSG', 'ALB', 'IT', 'MTB', 'ULTA', 'URI', 'WBA', 'PCG', 'CBRE', 'HIG', 'EIX', 'HPQ', 'TROW', 'TSCO', 'GWW', 'EFX', 'CDW', 'GPC', 'LEN', 'WBD', 'FANG', 'EBAY', 'VMC', 'ACGL', 'FITB', 'FTV', 'FE', 'WY', 'DTE', 'DAL', 'AEE', 'AVB', 'LYB', 'FRC', 'LH', 'PPL', 'GEHC', 'IR', 'HPE', 'MKC', 'ARE', 'ETR', 'MLM', 'RJF', 'WAT', 'HBAN', 'NDAQ', 'RF', 'CAH', 'ANSS', 'LUV', 'CFG', 'CHD', 'PFG', 'HOLX', 'EQR', 'PWR', 'XYL', 'DOV', 'CAG', 'NTRS', 'CTRA', 'TSN', 'EXR', 'VRSN', 'STE', 'VTR', 'TDY', 'CMS', 'WAB', 'K', 'CNP', 'DGX', 'EPAM', 'AMCR', 'DRI', 'MAA', 'OMC', 'PKI', 'MOH', 'CLX', 'EXPD', 'WST', 'SJM', 'AES', 'IEX', 'CINF', 'LVS', 'CF', 'TTWO', 'BALL', 'INVH', 'COO', 'MRO', 'KEY', 'STLD', 'BBY', 'TRGP', 'ALGN', 'J', 'BR', 'MOS', 'MPWR', 'FMC', 'SEDG', 'ATO', 'ETSY', 'AVY', 'INCY', 'TXT', 'SWKS', 'FDS', 'GRMN', 'WRB', 'HWM', 'FSLR', 'SYF', 'PAYC', 'NVR', 'EVRG', 'LDOS', 'VTRS', 'JBHT', 'IRM', 'LKQ', 'EXPE', 'PEAK', 'LW', 'IPG', 'TER', 'APA', 'NTAP', 'UAL', 'FLT', 'SIVB', 'RE', 'ZBRA', 'AKAM', 'LNT', 'HRL', 'ESS', 'BRO', 'IP', 'CBOE', 'KIM', 'TYL', 'JKHY', 'TECH', 'PTC', 'TRMB', 'NDSN', 'SNA', 'PKG', 'GEN', 'DPZ', 'POOL', 'MTCH', 'TFX', 'EQT', 'RCL', 'CPT', 'SWK', 'UDR', 'L', 'BF.B', 'MGM', 'CPB', 'MKTX', 'CHRW', 'HST', 'HSIC', 'CE', 'PHM', 'NI', 'WDC', 'CRL', 'GL', 'MAS', 'BBWI', 'EMN', 'STX', 'KMX', 'LYV', 'JNPR', 'BWA', 'TPR', 'UHS', 'WYNN', 'ALLE', 'FOXA', 'VFC', 'REG', 'PARA', 'QRVO', 'TAP', 'AAP', 'BIO', 'CDAY', 'BXP', 'CZR', 'HII', 'WRK', 'AAL', 'CCL', 'CMA', 'IVZ', 'ROL', 'FFIV', 'PNW', 'CTLT', 'RHI', 'WHR', 'HAS', 'AOS', 'PNR', 'FRT', 'NRG', 'BEN', 'ZION', 'SEE', 'NWSA', 'OGN', 'XRAY', 'SBNY', 'AIZ', 'DXC', 'GNRC', 'MHK', 'ALK', 'NWL', 'NCLH', 'LUMN', 'RL', 'LNC']

histwriter = pd.ExcelWriter('FIle_path', engine = 'openpyxl', mode = 'a', if_sheet_exists = 'overlay')
divwriter = pd.ExcelWriter('FIle_path', engine = 'openpyxl', mode = 'a', if_sheet_exists = 'overlay')


for j in range(len(keys)):
    stock = keys[j]
    histindice = 0
    divindice = 0
    for i in range(len(histcolumns)):
        if histcolumns[i] == stock:
            histindice = i
    for i in range(len(divcolumns)):
        if divcolumns[i] == stock:
            divindice = i

    #will not update for BRK.B and BF.B bc data is not there
    try:
        histstock_col=histfile[histcolumns[histindice-1]].dropna(axis=0)
    except NameError:
        print(f'I was unable to update history and dividends data for {stock}')
    start = histstock_col.iloc[-1]
    end = datetime.datetime.today()

    histnew_data = si.get_data(f'{stock}', start_date=start, end_date=end).drop(columns='ticker', axis=1)
    histnew_data.to_excel(histwriter, index = True, header = False, startrow = histstock_col.index[-1]+1, startcol=histindice)

    #Use exception handling again for companies that do not issue dividends 
    try:
        divstock_col=divfile[divcolumns[divindice-1]].dropna(axis=0)
    except NameError:
        print(f'I was unable to update dividends data for {stock}')
    start = divstock_col.iloc[-1]
   
    divnew_data = si.get_dividends(f'{stock}', start_date=start, end_date=end).drop(columns='ticker', axis=1)
    divnew_data.to_excel(divwriter, index = True, header = False, startrow = divstock_col.index[-1]+1, startcol=divindice)

histwriter.close()
divwriter.close()

print('History and dividends data has been updated successfully.')
