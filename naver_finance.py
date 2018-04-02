from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import codecs

def get_code_KRX(keyword):
    print("코드를 찾는 중입니다.")
    df_code = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    df_code.종목코드 = df_code.종목코드.map('{:06d}'.format)
    names = df_code['회사명'].tolist()
    codes = df_code['종목코드'].tolist()
    code = "None"
    for i in range(0,len(codes)):
        if keyword == names[i]:
            code = codes[i]
            break
    if code == "None":
        for i in range(0,len(codes)):
            if keyword in names[i]:
                code = codes[i]
                break
    print("종목코드: {}".format(code))
    return code

def finance_extract_naver(code,start, end):
    total_page = (int(str(end - start).split(' ')[0])+1) // 10 + 1
    url = "http://finance.naver.com/item/sise_day.nhn?code="+code
    df = pd.DataFrame() 
    for page in range(1, total_page+1):
        pg_url = '{url}&page={page}'.format(url=url, page=page)
        df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)
    return df


def finance_eval(df, start, end):
    recent_data = df.iloc[[0]]
    prev_data = df.iloc[[1]]

    openval = int(str(recent_data.to_dict().get('시가')[0]))
    highval = int(str(recent_data.to_dict().get('고가')[0]))
    lowval = int(str(recent_data.to_dict().get('저가')[0]))
    closeval = int(str(recent_data.to_dict().get('종가')[0]))
    volume = int(str(recent_data.to_dict().get('거래량')[0]))
    yesterday = int(str(prev_data.to_dict().get('종가')[1]))
    diff = closeval - yesterday
    percent = diff/yesterday * 100
    print("전일대비: {:,} ".format(diff),end='')
    print("(%.2f%%)" %percent)
    print("시가: {:,}".format(openval))
    print("고가: {:,}".format(highval))
    print("저가: {:,}".format(lowval))
    print("종가: {:,}".format(closeval))

    return (diff, percent, openval, highval, lowval, closeval)
    
def finance_plot(df, start, end):
    df['날짜'] = pd.to_datetime(df['날짜'],format='%Y.%m.%d')
    df = df.sort_values(by='날짜')
    df = df.set_index('날짜')
    mask = (df.index.to_pydatetime() > start) & (df.index.to_pydatetime() <= end)
    to_plot = df.loc[mask]
    plt.plot(to_plot.index.to_pydatetime(), to_plot['종가'])
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
        reader = codecs.getreader("utf-8")
        data = json.loads(reader(res).read())
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
    code = get_code_KRX(keyword)
    fss_list = dart_extract(code,start,end)
    df_finance = finance_extract_naver(code, start,end)

    finance_data = finance_eval(df_finance, start, end)
    finance_plt = finance_plot(df_finance, start, end)
    #finance_plt.show()
    #finance_plt.savefig(keyword+".jpg")






                 
