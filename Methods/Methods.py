import numpy as np
import math


def grcheck(format1, format2, group):
    while True:
        var = input(f"Th{format1} the entered group id{format2}: {group[:]} \n Confirm? (y/n) >")
        if var == "y":
            break
        elif var == "n":
            group = [
                int(x)
                for x in input(
                    "\nPlease enter a group id (where 000019 is 19) \n If entering multiple group ids, separate each by a single space.> "
                ).split(" ")
            ]
    return group


def startcol_finder(df):
    x = df.columns
    for i in range(len(x)):
        try:
            if type(int(x[i][:4])) == type(2):
                return int(x[i][:4])
        except ValueError:
            continue


def ticks_norm(list, year):
    lst = []
    length = len(year)
    for i in range(len(list)):
        inter = int(list[i])
        try:
            if inter <= year[-1] and inter >= year[0] and inter != year[-2]:
                lst += [inter]
        except IndexError:
            continue
    lst = np.unique(lst).tolist()
    if length <= 14:
        lst += [year[-2]]
    if length > 14:
        for i in range(length):
            try:
                if lst[i] - lst[i - 1] == 1:
                    lst = lst[: (i - 1)] + lst[i:]
            except IndexError:
                continue

    return lst


def fix_date(df):
    df.reset_index(inplace=True)
    y = [str(date) for date in df["Date"]]
    df[["Date", "Delete"]] = [date.split(" ") for date in y]
    df.drop("Delete", axis=1, inplace=True)


def find_name(df):
    lst1 = []
    for x in range(len(df["shortName"])):
        app = df["shortName"][x].split(" ")[0]
        if app[-1] == ",":
            app = app[:-1]
        lst1 += [app]

    lst2 = []
    for i in range(len(lst1)):
        if lst1[i] not in lst2:
            lst2 += [lst1[i]]
    # assemble string
    string = ""
    for i in range(len(lst2)):
        if i == 0:
            string += f"{lst2[i]}"
        else:
            string += f"-{lst2[i]}"
    return string


def divide_by_five(interger):

    interger1 = str(int(math.fabs(interger * 1.05)))
    x = [a for a in interger1]
    y = int(x[1]) + (5 - int(x[1]))
    if y > int(x[1]):
        x = x[0] + f"{y}" + "".join(f"{int(a)*0}" for a in range(len(x) - 2))
    elif y < int(x[1]):
        x = str(int(x[0]) + 1) + "".join(f"{int(a)*0}" for a in range(len(x) - 1))
    else:

        x = x[0] + str(int(x[1]) + 1) + "".join(f"{int(a)*0}" for a in range(len(x) - 2))
    if int(interger) < 0:
        return int(x) * -1
    else:
        return int(x)


def rm_zeroes(data, years):
    count = 0
    while True:
        if data[0] == 0:
            data = data[1:]
            count += 1
        else:
            break
    years = years[(count):]
    return [data, years]


def resol(integer):
    if integer < 0:
        integer = 0
    return integer


# label check
def labelcheck(label):
    while True:
        var = input(f"This is the entered label: {label} \n Confirm? (y/n) >")
        if var == "y":
            break
        elif var == "n":
            label = input("Please enter the name for this group code:")
    return label
