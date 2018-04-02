from pandas_datareader import data, wb
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import fix_yahoo_finance as yf
import json
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_code(keyword):
    yf.pdr_override()
    print("코드를 찾는 중입니다.")
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome('chromedriver',chrome_options=options)
    driver.get("http://www.ksfc.co.kr/services/loan/avg/popup/codes.do")
    elem = driver.find_element_by_id('nameSearch')
    elem.send_keys(keyword)
    elem.submit()
    res = driver.page_source
    bs = BeautifulSoup(res,'html.parser')
    table = bs.find_all('table')[0]
    n_columns = 0
    n_rows = 0
    column_names = []

    for row in table.find_all('tr'):
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows+=1
        if n_columns == 0:
            n_columns = len(td_tags)
        th_tags = row.find_all('th') 
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())
    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0,n_columns)
    df_code = pd.DataFrame(columns = columns, index= range(0,n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df_code.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1
    driver.close()
    driver.quit()
    names = df_code['주식종목명'].tolist()
    codes = df_code['단축코드'].tolist()
    for i in range(0,len(codes)):
        if names[i] == keyword:
            code = codes[i]
            break
    return code
    
def finance_extract(code, start, end):
    print("데이터를 가져오는 중입니다.")
    df = data.get_data_yahoo(code+".KS",start,end)
    if df.empty:
        print("데이터 가져오기 실패")
    return df
def finance_eval(df, start, end):
    recent_data = df.iloc[[-1]]
    prev_data = df.iloc[[-2]]

    openval = float(str(recent_data.to_dict().get('Open')).split('):')[1].split('}')[0])
    highval = float(str(recent_data.to_dict().get('High')).split('):')[1].split('}')[0])
    lowval = float(str(recent_data.to_dict().get('Low')).split('):')[1].split('}')[0])
    closeval = float(str(recent_data.to_dict().get('Close')).split('):')[1].split('}')[0])
    adjcloseval = float(str(recent_data.to_dict().get('Adj Close')).split('):')[1].split('}')[0])
    volume = float(str(recent_data.to_dict().get('Volume')).split('):')[1].split('}')[0])
    yesterday = float(str(prev_data.to_dict().get('Adj Close')).split('):')[1].split('}')[0])
    total = adjcloseval * volume
    diff = adjcloseval - yesterday
    percent = diff/yesterday * 100
    print()
    print("시가 : {:,} KRW".format(int(adjcloseval)))
    print("전일대비: {:,} ".format(int(diff)),end='')
    print("(%.2f%%)" %percent)
    print("시작: {:,}".format(int(openval)))
    print("최고: {:,}".format(int(highval)))
    print("최저: {:,}".format(int(lowval)))
    print("종료: {:,}".format(int(closeval)))

    return (int(adjcloseval),int(diff), percent, int(openval), int(highval), int(lowval),int(closeval))
    
def finance_plot(df, start, end):
    mask = (df.index.to_pydatetime() > start) & (df.index.to_pydatetime() <= end)
    to_plot = df.loc[mask]
    plt.plot(to_plot.index.to_pydatetime(), to_plot['Adj Close'])
    return plt

def dart_extract(code, start, end):
    auth = "27445d28e3917e9772318feddcb787b0c2f42543"
    start_dt = start.strftime('%Y%m%d')
    end_dt = end.strftime('%Y%m%d')
    url = "http://dart.fss.or.kr/api/search.json?auth={}&crp_cd={}&start_dt={}&end_dt={}&page_set=100&page_no=".format(auth,code, start_dt, end_dt)
    page_num = 1
    total_page = -1
    selected = []
    fss_list = []
    while page_num != total_page+1:
        res = urlopen(url+str(page_num))
        data = json.loads(res.read())
        df =  pd.read_json(json.dumps(data))
        temp = df['list'].tolist()
        selected += temp
        total_page = int(df.iloc[[0]].to_dict().get('total_page')[0])
        page_num+=1

    for data in selected:
        url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+data['rcp_no']
        fss_list.append((data['rpt_nm'],url))
    print("공시 정보 수: {}".format(len(fss_list)))
    return fss_list

if __name__ == '__main__':
    keyword = input("회사 이름: ")
    start = input("조회 시작일: ")
    if start == '':
        start = '2017-01-01'
    start = datetime(int(start.split('-')[0]),int(start.split('-')[1]),int(start.split('-')[2]))
    end = datetime.now()
    code = get_code(keyword)
    fss_list = dart_extract(code,start,end)

    df_finance = finance_extract(code, start,end)
    finance_data = finance_eval(df_finance, start, end)
    finance_plt = finance_plot(df_finance, start, end)
    finance_plt.show()






                 
