from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import pymysql as psql
import sys
import os

last_success = 0

conn = psql.connect(host='localhost', db='***************', user='***************', password='***************',charset='utf8')
query = "REPLACE INTO MK_NEWS (seq_no,date,location) VALUES (%s,%s,%s);"
cur = conn.cursor()

start = time.time()
stopwords = {'[',']',',',', ','\n'}
flag=0

try:
    fp_log = open("mk_limit.txt","r")
    seq_no = int(fp_log.readline())
    last_success = seq_no
    fp_log.close()
except:
    seq_no = 1
    last_success = 1

while True: 
    try:
        res = urlopen("http://news.mk.co.kr/newsRead.php?sc=30000001&year=2018&no="+str(seq_no)).read().decode('cp949', 'ignore')
        bs = BeautifulSoup(res,'html.parser')
        title_section = bs.find_all('div',class_='news_title')[0]

        title = str(title_section.find_all('h1',class_='top_title')[0]).split('<h1 class="top_title">')[1].split('</h1>')[0]

        date = title_section.find_all('li',class_='lasttime1')
        if len(date) == 0:
            date = title_section.find_all('li',class_='lasttime')
        date = str(date[0]).split('</li>')[0].split(': ')[1].split(' ')[0].replace('.','-')

        article = str(bs.find_all('div',class_='left_content')[0].find_all('div',class_='art_txt')).split('<!--이미지 키우는 스크립트-->')[0]
        article = article.replace('<',';`!@').replace('>',';`!@').replace('googletag.display(',';`!@').replace(');',';`!@')
        strings = article.split(';`!@')
        sflag = 1
        result = []
        for string in strings:
            if sflag == 0:
                sflag = 1
            else:
                sflag = 0
                if string not in stopwords:
                    result.append(string)        
        article = '\n'.join(result)
        if not os.path.isdir('crawled'):
            os.mkdir('crawled')
        if not os.path.isdir('crawled/mk_news'):
            os.mkdir('crawled/mk_news')
        if not os.path.isdir('crawled/mk_news/'+date):
            os.mkdir('crawled/mk_news/'+date)

        location = 'crawled/mk_news/'+date+'/'+str(seq_no)+'.txt'
        content = (str(seq_no),date,location)
        cur.execute(query,content)
        conn.commit()

        fp = open(location,'w')
        print(title,file=fp)
        print('\n',file=fp)
        print(article,file=fp)
        fp.close()
        sys.stdout.write("\rTotal: %d" %(seq_no)),
        sys.stdout.flush()
        last_success = seq_no
        seq_no+=1

    except Exception as e:
        if flag > 1000:
            fp_log = open("mk_limit.txt","w")
            print(last_success,file=fp_log)
            fp_log.close()
            break
        else:
            seq_no+=1
            flag+=1;
            continue
    flag = 0    
       
print("\nExecution time = {0:.5f}".format(time.time() - start))
cur.close()
conn.close()




