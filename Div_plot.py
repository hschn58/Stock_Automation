import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl


    
file_path=r'FILE_PATH'
save_loc = r'FILE_PATH'


divdata =pd.read_excel(file_path)
#histdata = pd.read_excel(file_path)

divcols = divdata.columns
#histcols = histdata.columns



while True:
    while True:
        ticker = input('Please enter a stock ticker to graph dividends: ').upper()
        if divcols.tolist().count(ticker)==1:
            break
        if divcols.tolist().count(ticker)==0:
            print('\n')
            print('####################')
            print('Stock not available.')
            print('####################')
            print('\n')
        # if histcols.tolist().count(ticker)==1 and divcols.tolist().count(ticker)==0:
        #     subplots = 1
        #     break
    # for i in range(len(histcols)):
    #     if histcols[i]==ticker:
    #         histindice = i
    plt.ion()
    plt.figure(figsize=[7., 7.])
    # if subplots == 1:
    #     plt.figure(figsize=[7., 7.])
    #     plt.plot(histdata[histcols[histindice-1]].dropna(axis=0).drop(index=[0,1]), histdata[f'{ticker}'].dropna(axis=0).drop(index=0), linewidth=1.5, zorder=3)
    #     plt.title(f'{ticker} Price History')
    #     plt.grid(axis='y',linewidth=0.5, zorder=0)

    # if subplots == 2:
    #     plt.subplot(1,2,1)
    #     plt.plot(histdata[histcols[histindice-1]].dropna(axis=0).drop(index=[0,1]), histdata[f'{ticker}'].dropna(axis=0).drop(index=0), linewidth=1.5, zorder=3)
    #     plt.title(f'{ticker} Price History')
    #     plt.grid(axis='y',linewidth=0.5, zorder=0)
        

    for i in range(len(divcols)):
        if divcols[i]==ticker:
            divindice = i

    # plt.subplot(1,2,2)
    plt.plot(divdata[divcols[divindice-1]].dropna(axis=0).drop(index=[0,1]), divdata[f'{ticker}'].dropna(axis=0).drop(index=0), linewidth=1.5, zorder=3)
    plt.title(f'{ticker} DPS Over Time')
    plt.grid(axis='y',linewidth=0.5, zorder=0)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('${x:1.2f}'))


    save = input("Save Figure? (y/n): ")

    while True:
        try:
            save = save.upper()
        except AttributeError:
            print("Please enter 'y' or 'n': " )
            continue 
        if save=='Y':

            import os
            os.chdir(save_loc)

            plt.savefig(f'{ticker} DPS Over Time.pdf')

            break
        if save=='N':
            break
        save = input("Save Figure? (y/n): ")


    session = input("Continue session? (y/n): ")

    while True:
        try:
            session = session.upper()
        except AttributeError:
            print("Please enter 'y' or 'n': " )
            continue 
        if session=='Y':
            plt.savefig(f'{ticker} DPS Over Time.pdf')
            break
        if session=='N':
            break
        session = input("Continue session? (y/n): ")
    
    if session=='N':
        break


