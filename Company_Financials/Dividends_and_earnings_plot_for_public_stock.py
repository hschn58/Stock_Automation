# plot company dividends and earnings from web-scraped tabular data

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys


ticker = input("Please input a stock ticker:")
ticker = ticker.upper()
dividends = pd.read_excel(r"DIV_FILE")
earnings = pd.read_excel(r"DIV_FILE")

x = earnings["startdatetime"]
earnings[["startdatetime", "Delete"]] = x.str.split("T", expand=True)
earnings.drop("Delete", axis=1, inplace=True)
earnings["startdatetime"] = pd.to_datetime(earnings["startdatetime"])

dividends["Date"] = pd.to_datetime(dividends["Date"])

div = dividends[(dividends["Stock"] == ticker) & (dividends["Date"].dt.year > 1999)].dropna()
earn = earnings[
    (earnings["ticker"] == ticker) & (earnings["startdatetime"].dt.year > 1999)
].dropna()

i = div["Date"].dt.year.min()
i1 = earn["startdatetime"].dt.year.min()
list = []
list1 = []
while i < datetime.now().year:
    year = div[div["Date"].dt.year == i]["Dividends"].sum()
    list.append(year)
    i = i + 1

while i1 < datetime.now().year:
    year1 = earn[earn["startdatetime"].dt.year == i1]["epsactual"].sum()
    list1.append(year1)
    i1 = i1 + 1

annual_dividends = [float("{:.2f}".format(number)) for number in list]
annual_earnings = [float("{:.2f}".format(number)) for number in list1]

div1 = pd.DataFrame()
earn1 = pd.DataFrame()


earn1["Earnings"] = annual_earnings
earn1["Year"] = range(earn["startdatetime"].dt.year.min(), datetime.now().year)

div1["Dividends"] = annual_dividends
if len(div1) == 0:
    fig, ax = plt.subplots()
    plt.bar(
        earn1["Year"], earn1["Earnings"], color=["blue"], label="Earnings per share", width=0.25
    )
    plt.legend(loc="upper left")
    plt.ylabel("Dollars per share")
    plt.title(ticker)
    ax.axhline(color="black", linewidth=0.51)
    plt.tight_layout()
    plt.savefig(PATH)
    plt.show()
    sys.exit()
else:
    div1["Year"] = range(div["Date"].dt.year.min(), datetime.now().year)
    ax1 = plt.subplot(2, 1, (1, 2))
    plt.plot(div1["Year"], div1["Dividends"])

    # plot yearly data
    ax = plt.subplot(2, 1, (1, 2), sharey=ax1, sharex=ax1)
    plt.bar(
        earn1["Year"] + 0.000,
        earn1["Earnings"],
        color=["blue"],
        label="Earnings per share",
        align="edge",
        width=0.25,
    )
    plt.bar(
        div1["Year"] + 0.25,
        div1["Dividends"],
        color=["orange"],
        label="Dividend per share",
        align="edge",
        width=0.25,
    )
    plt.legend(loc="upper left")
    plt.ylabel("Dollars per share")
    ax.axhline(color="black", linewidth=0.51)
    plt.title(ticker)
    plt.tight_layout()
    plt.savefig(PATH)  # save the figure
    plt.show()
