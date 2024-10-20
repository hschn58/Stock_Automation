#creates a chart of customer account value, account percent change, and yearly net deposits/withdrawals.

from Methods import grcheck, startcol_finder
import pandas as pd
import os
import datetime 
import numpy as np


data_path =r"ADD PATH"
save_loc = r"ADD PATH"
file_name = r"ADD PATH"

os.chdir(data_path)
var1 = pd.read_excel(file_name, header = 0)

upper = datetime.datetime.today().year
while True:
    while True:
        try:
            group = [int(x) for x in input("\nPlease enter a group id (where 000019 is 19) \nIf entering multiple group ids, separate each by a single space.> ").split(' ')]
            if len(group)==1:
                format1='is is'
                format2=''
            else:
                format1='ese are'
                format2='s'
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
            year=[]
            NetDepWD=[]
            
            lower=startcol_finder(var)
            for i in range(lower, upper+1):
                try:
                    sum1 = sum(var[f'{i}ClosingBal'])
                    
                except KeyError:
                    sum1 = 'd'
                if sum1 != 'd':
                    value+=[sum1]
                    year+=[i]
                try:
                    sum2 = sum(var[pd.DataFrame(var.columns)[0][pd.DataFrame([x[-12:] for x in var.columns])[0]==f'{i}NetDepWD']].reset_index().iloc[:,-1])
                except KeyError:
                    sum2='N'
                if sum2!='N':
                    NetDepWD+=[sum2]
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
    
    #add label here so that it is assigned before chart is created
    
    label = input('Please enter the name for this group code:')
    label = labelcheck(label)
    #year bounds

    lower = startcol_finder(var)

    value1=[]
    year1=[]
    for i in range(lower, upper+1):
        try:
            summ = sum(x for x in var[f'{i}AdjOpenBal'])
        except KeyError:
            summ = 0
        except IndexError:
            summ = 0
        if summ!=0:
            value1+=[summ]
            year1+=[i]

    
    years = [str(x) for x in year[-5:]]
    if years[-1] != str(upper):
        years += [str(upper)]
        years.remove(f'{years[0]}')
        
    #given years for account value, get indice associated w that year for the adjopeningbalance
    indices = []

    length=len(years)

    for i in range(length):
        for j in range(len(year1)):
            if year1[j]==int(years[i]):
                indices+=[j]
    names = {'index': 'Year', 'Account Value': 'Account Value', 'Percent Change': 'Percent Change'}
    chart = pd.DataFrame(columns=years, index = ['Account Value', 'Percent Change', 'Deposits/Withdrawals']).reset_index()
    chart.rename(columns=names, inplace=True)
    

    #creating chart, would like last 4 years of entries but take as many as there is

    for i in range(length-1):
        chart[years[i]].iloc[0]=value[(-length+1)+i]

    chart[years[-1]].iloc[0]=sum(x for x in var['Current Value'])

    for i in range(length-1):
        chart[years[i]].iloc[1]=((chart[years[i]].iloc[0]/value1[indices[i]])-1)*100

    chart[years[-1]].iloc[1]=((chart[years[-1]].iloc[0]/value1[-1])-1)*100
    
    for i in range(length):
        chart[years[i]].iloc[2]=NetDepWD[(i-length)]

    #formatting text to look like currency/correct rounding
    for i in range(length): 
        chart[years[i]].iloc[0]="${:,.2f}".format(chart[years[i]].iloc[0])

    for i in range(length): 
        chart[years[i]].iloc[1]="{:.2f}%".format(chart[years[i]].iloc[1])
    
    for i in range(length): 
        chart[years[i]].iloc[2]="${:,.2f}".format(chart[years[i]].iloc[2])
    
    cell_text=[]
    for row in range(len(chart)):
        cell_text.append(chart.iloc[row])

    import matplotlib.pyplot as plt
    import textwrap as twp

    plt.ion()
    plt.figure(figsize=[10., 5.])

    lst = chart.columns.tolist()
    columns = [twp.fill(X,11) for X in lst]
    Chartdata=plt.table(cellText=cell_text, colLabels=columns, loc='center')
    Chartdata.auto_set_font_size(True)

    # Set Cell Size (Optional)

    for col in range(0, len(lst)):
        cell = Chartdata[0, col]
        cell.set_height(0.25)
        cell = Chartdata[1, col]
        cell.set_height(0.25)
        cell = Chartdata[2, col]
        cell.set_height(0.25)
        cell= Chartdata[3, col]
        cell.set_height(0.25)

    empty = np.array([])
    plt.xticks(empty)
    plt.yticks(empty)

    ax = plt.gca()
    ax.spines[["right", "top", "left", "bottom"]].set_visible(False)
    

    plt.title(f"{label} \n Performance Chart")
    plt.tight_layout()

    save = input("Save Figure? (y/n): ")

    while True:
        try:
            save = save.upper()
        except AttributeError:
            print("Please enter 'y' or 'n': " )
            continue 
        if save=='Y':

            os.chdir(save_loc)

            plt.savefig(f'{label} Performance Chart.pdf')
            
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
        if session=='Y' or session=='N':
            break
        session = input("Continue session? (y/n): ")
    
    if session=='N':
        break

    
