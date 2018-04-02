from datetime import datetime
import pandas as pd
import json
import time
from urllib.request import urlopen
from urllib.request import urlretrieve


def NASDAQ_code():
    url = "https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
    res = urlretrieve(url,"companylist.csv")
    company_list = open("companylist.csv",'r').readlines()
    company_dict = {}
    fullname_list = []
    for i in range(1,len(company_list)):
        temp = company_list[i].split(',')
        symbol = temp[0]
        name = temp[1].lower()
        quote = temp[7]
        company_dict[name] = (symbol,quote)
        fullname_list.append(name)

    return company_dict, fullname_list

def symbol_search(name,company_dict,fullname_list):

    fullname = ''
    for full in fullname_list:
        if name in full:
            fullname = full
            break
    if fullname == '':
        print("Symbol not found.")
        return None
    result = company_dict[fullname]
    return result

if __name__ =='__main__':
    company_dict, fullname_list = NASDAQ_code()
    input_val = input("name: ")
    raw_data = symbol_search(input_val,company_dict,fullname_list)
    symbol = raw_data[0]
    quote = raw_data[1]
    print("symbol: {}".format(symbol))
    print("summary quote: {}".format(quote))
