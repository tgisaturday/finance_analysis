from datetime import datetime
import pandas as pd
import json
import time
from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import codecs
import slate

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

def dart_extract(code, start, end):
    
    auth = "************************************************"
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
        rcp_no = data['rcp_no']
        url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+rcp_no
        res = urlopen(url).read()
        bs = BeautifulSoup(res,'html.parser')
        href =bs.find_all(href=True)
        for a in href:
            if a['href'] == "#download":
                dcm_no = a['onclick'].split(';')[0].split(", '")[1].split("'")[0]
                break
        url = "http://dart.fss.or.kr/pdf/download/pdf.do?rcp_no=" + rcp_no +"&dcm_no=" + dcm_no
        fss_list.append((data['rpt_nm'],url))
        break
    print("공시 정보 수: {}".format(len(fss_list)))
    res = urlretrieve(fss_list[0][1],"./temp.pdf")
    #file = open("temp.pdf", 'wb')
    #print(res)
    #file.write(res.content)
    #file.close()
    doc = slate.PDF(open('temp.pdf','rb'))
    for i in range(len(doc)):
        print(doc[i])
    return fss_list

if __name__ == '__main__':
    #keyword = input("회사 이름: ")
    #start = input("조회 시작일: ")
    start = '2017-01-01'
    start = datetime(int(start.split('-')[0]),int(start.split('-')[1]),int(start.split('-')[2]))
    #start = datetime.now()
    end = datetime.now()
    #code = get_code_KRX(keyword)
    code='005930'
    fss_list = dart_extract(code,start,end)

    #finance_plt.show()
    #finance_plt.savefig(keyword+".jpg")






                 
