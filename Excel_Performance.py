#creates a customer performance overview sheet from long-term investment data.

#asset arrival date for lower 
from Methods import startcol_finder, grcheck, ticks_norm, rm_zeroes, labelcheck
import pandas as pd
import datetime 
import math
import os
import numpy as np
import warnings

file_path=r"ADD_PATH"
save_loc=r"ADD_PATH"
data_file=r"ADD_PATH"

os.chdir(file_path)
var1 = pd.read_excel(data_file, header = 0)

upper = datetime.datetime.today().year
while True:
    warnings.filterwarnings('ignore')
    while True:
        try:
            group = [int(x) for x in input("\nPlease enter a group id (where 000019 is 19) \nIf entering multiple group ids, separate each by a single space.> ").split(' ')]
            if len(group)==1:
                format1='is is'
                format2=''
            else:
                format1='ese are'
                format2='s'

            #check correct group 

            group = grcheck(format1,format2,group)
            
            groupstring=[]
            if len(group)>1:
                format1='ese are'
                format2='s'
                for i in range(len(group)):
                    x=var1[var1['groupld']==group[i]]
                    y=x[x['Status']=='Active']
                    if len(y)>0:
                        groupstring+=[y]
                try:
                    var = pd.concat(groupstring, axis=0, ignore_index=True, keys=var1.columns.tolist())
                except ValueError:
                    var = pd.DataFrame(columns=['2022ClosingBal'])
            else:
                var2 = var1[var1['groupld']==group[0]]
                var = var2[var2['Status']=='Active']
            if len(group)==1:
                format1='is is'
                format2=''
            value=[]
            year1=[]
            
            lower=startcol_finder(var)
            for i in range(lower, upper+1):
                try:
                    summ = sum(var[f'{i}ClosingBal'])
                except KeyError:
                    summ = 'd'
                if summ!='d':
                    value+=[summ]
                    year1+=[i]
            
            value+=[sum(var['Current Value'])]
            year1+=[upper]

            #check groupid entered is valid 

            if len(group)==0:
                print('\n')
                print('##########################')
                print("No group id was entered.")
                print('##########################')
            elif sum(value) == 0:
                print('\n')
                print('##########################')
                print('This group id has no data')
                print('##########################')
            else:
                break    
        except ValueError:
            print('\n')
            print('#######################################')
            print('Group ids must be entered as integers.')
            print('#######################################')
            continue

    #assign label here so that the label has been assigned before chart pops up 

    label = input('Please enter the name for this group code:')
    label = labelcheck(label)


    #plot
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib as mpl

    #constrained layout worked better than plt.tight_layout()
    plt.ion()
    fig = plt.figure(figsize=[10.,8.], layout='constrained')

    #Columns all integer muliples of each other 
    ax1 = plt.subplot2grid((5,10), (1,6), colspan=4, rowspan=2)

    yr=np.array(year1)

    dat = rm_zeroes(np.array(value), yr)
    ydat = dat[0]
    xdat = dat[1]

    plt.grid(axis='y',linewidth=0.5, zorder=0)
    plt.bar(xdat, ydat, zorder=3)

    ax = plt.gca()
    ax.ticklabel_format(style='plain')
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    plt.xticks(rotation=90)
    plt.xticks(ticks_norm(list(plt.xticks()[0])+year1[-3:], year1))
    if len(var)>1:
        plurality='(s)'
    else:
        plurality=''
    #title
    plt.title(f"Account{plurality} Value")


    ######################################################
    #Cumulative gain/loss

    #obtain data

    ax2 =  plt.subplot2grid((5,10), (1,0), colspan=3, rowspan=4)

    value1=[]
    year=[]
    for i in range(lower, upper):
        try:
            summ = sum(var[f'{i}ClosingBal'])-sum(var[f'{i}AdjOpenBal'])+value1[-1]
        except KeyError:
            summ =0
        except IndexError:
            summ = sum(var[f'{i}ClosingBal'])-sum(var[f'{i}AdjOpenBal'])
        if summ!=0:
            value1+=[summ]
            year+=[i]

    value1+= [sum(var['Current Value'])-sum(var[f'{upper}AdjOpenBal'])+value1[-1]]
    year+=[upper]

    if value1[-1]>value1[0]:
        delta='Gain'
    else:
        delta='Gain/Loss'

    yr=np.array(year)

    dat = rm_zeroes(np.array(value1), yr)
    ydat = dat[0]
    xdat = dat[1]

    plt.grid(axis='y',linewidth=0.5, zorder=0)
    plt.bar(xdat, ydat, zorder=3, bottom=0)

    ax = plt.gca()
    ax.ticklabel_format(style='plain')
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    plt.xticks(rotation=90)
    plt.xticks(ticks_norm(list(plt.xticks()[0])+year[-3:], year))



    #title
    plt.title(f"Cumulative {delta}")

    ######################################################
    #DEP / WD

    #obtain data
    ax3 = plt.subplot2grid((5,10), (3,6), colspan=4, rowspan=2)

    value2=[]
    year=[]
    for i in range(lower, upper+1):
        try:
            summ = sum(var[pd.DataFrame(var.columns)[0][pd.DataFrame([x[-12:] for x in var.columns])[0]==f'{i}NetDepWD']].reset_index().iloc[:,-1])
        except KeyError:
            summ ='d'
        if summ!='d':
            value2+=[summ]
            year+=[i]
    

    yr=np.array(year)

    dat = rm_zeroes(np.array(value2), yr)
    ydat = dat[0]
    xdat = dat[1]

    plt.grid(axis='y',linewidth=0.5, zorder=0)
    plt.bar(xdat, ydat, zorder=3, bottom=0)
    plt.axhline(color = 'black', linewidth=0.51)


    ax = plt.gca()
    ax.ticklabel_format(style='plain')
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    plt.xticks(rotation=90)
    plt.xticks(ticks_norm(list(plt.xticks()[0])+year[-3:], year))

    #title
    plt.title("Deposits and Withdrawals by Year")

    ######################################################
    #Cumulative Deposit and Withdrawals


    data = pd.DataFrame(value2, index=yr)

    value3=[]
    year=[]
    for i in range(lower, upper+1):
        try:
            summ = data[0][i]+sum(data[0][:(i-lower)])
        except KeyError:
            summ = 0
        except IndexError:
            try:
                summ = data[0][i]
            except IndexError:
                summ ='d'
        if summ!='d':
            value3+=[summ]
            year+=[i]


    ax4 = plt.subplot2grid((5,10), (1,3), colspan=3, rowspan=4)
    
    yr=np.array(year)

    dat = rm_zeroes(np.array(value3), yr)
    ydat = dat[0]
    xdat = dat[1]

    plt.grid(axis='y',linewidth=0.5, zorder=0)
    plt.plot(xdat, ydat, linewidth=2, zorder=3)

    plt.axhline(color = 'black', linewidth=0.51)


    ax = plt.gca()
    ax.ticklabel_format(style='plain')
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    plt.xticks(rotation=90)
    plt.xticks(ticks_norm(list(plt.xticks()[0])+year[-3:], year))
    plt.title("Cumulative Deposits \n and Withdrawals")

    chart = pd.DataFrame(columns=['Asset Arrival Date', 'Opening Balance', 'Cumulative Deposits and Withdrawals', 'Adjusted Opening Balance', 'Current Value', f'Cumulative {delta}','Account Percent Change'], index = [0])
    chart["Asset Arrival Date"][0]=str(min(var['assetArrivalDate'])).split(' ')[0]
    chart['Opening Balance'][0]=round(sum(var['assetsAtArrival']),2)

    chart['Cumulative Deposits and Withdrawals'][0]=round(value3[-1],2)
    chart['Adjusted Opening Balance'][0]=round(value3[-1]+chart['Opening Balance'][0],2)
    chart['Current Value'][0]=round(value[-1],2)
    chart[f'Cumulative {delta}']=round(value1[-1],2)
    chart['Account Percent Change'][0]=str(round(100*(value[-1]-chart['Adjusted Opening Balance'][0])/math.fabs(chart['Adjusted Opening Balance'][0]), 2))+'%'

    lst = chart.columns.tolist()
    for i in range(1,len(lst)-1): 
        chart[lst[i]][0]="${:,.2f}".format(chart[lst[i]][0])
    cell_text=[]
    for row in range(len(chart)):
        cell_text.append(chart.iloc[row])

    ax5 = plt.subplot2grid((5,10), (0,0), colspan=10, rowspan=1)

    import textwrap as twp

    columns = [twp.fill(X,11) for X in lst]
    Chartdata=plt.table(cellText=cell_text, colLabels=columns, loc='center')
    Chartdata.auto_set_font_size(True)
    for r in range(0, len(lst)):
        cell = Chartdata[0, r]
        cell.set_height(0.7)
    for r in range(0, len(lst)):
        cell = Chartdata[1, r]
        cell.set_height(0.25)
    empty = np.array([])
    plt.xticks(empty)
    plt.yticks(empty)
    ax5.spines[["right", "top", "left", "bottom"]].set_visible(False)

    #label 
    

    plt.title(f"{label} \n Performance Overview")

    #save
    save = input("Save Figure? (y/n): ")

    while True:
        try:
            save = save.upper()
        except AttributeError:
            print("Please enter 'y' or 'n': " )
            continue 
        if save=='Y':

            os.chdir(save_loc)

            plt.savefig(f'{label} Performance Overview.pdf')
            
            break
        if save=='N':
            break
        save = input("Save Figure? (y/n): ")

    #session
    session = input("Continue session? (y/n): ")

    while True:
        try:
            session = session.upper()
        except AttributeError:
            print("Please enter 'y' or 'n': " )
            continue 
        if session=='Y' or session=='N':
            break
        session = input("Continue session? (y/n): ")
    
    if session=='N':
        break
