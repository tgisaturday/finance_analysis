from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import pymysql as psql
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawler(sid,date):
    print("sid[%s] :: Start Crawling"%(sid))
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')

    conn = psql.connect(host='localhost', db='***************', user='***************', password='***************',charset='utf8')
    query = "REPLACE INTO news_total (seq_no,date,naver_link,original_link,sid,company,upload_date,title,text) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    cur = conn.cursor()
    start = time.time()
    flag=0

    page = 1
    link_list = []
    flag = 0
    while True: 
        try:
            driver = webdriver.Chrome('chromedriver',chrome_options=options)
            driver.get("http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=" + str(sid) + "#&date=" + str(date) + " 00:00:00&page="+str(page))
            res = driver.page_source
            bs = BeautifulSoup(res,'html.parser')
            real_page = int(str(bs.find_all('div',class_='paging')[0].find_all("strong")[0]).replace("<strong>","").replace("</strong>",""))
            if real_page != page:
                driver.close()
                break
            link_section = bs.find_all('div',class_="section_body")[0]
            for a in link_section.find_all('a', href=True):
                if str(a['href']).split('?')[1].split('&')[0]=="mode=LSD":
                    link_list.append("http://news.naver.com/"+str(a['href']))
            sys.stdout.write("\rExtracting links from page: %d" %(page)),
            sys.stdout.flush()
            page += 1
            driver.close()
        except Exception as e:
            if flag > 10:
                print(e)
                break
            else:
                flag+=1
                continue
        flag = 0
    idx=1
    print()
    for link in link_list:
        try:
            driver = webdriver.Chrome('chromedriver',chrome_options=options)
            driver.get(link)
            res = driver.page_source

            bs = BeautifulSoup(res,'html.parser')
            meta = bs.find_all('meta',property="me2:category1")[0]['content']
            title_section = bs.find_all('div',class_='article_info')[0]
            title = title_section.find_all('h3',id="articleTitle")[0].text
            article = bs.find_all('div',id="articleBodyContents")[0].text.split("function _flash_removeCallback() {}")[1].replace('\n','').replace('\t','')
            sponsor_section = bs.find_all('div', class_="sponsor")[0]
            upload_date = sponsor_section.find_all('span', class_="t11")[0].text
            original = sponsor_section.find_all('a',href=True)[0]['href']
            naver_link = link
            uploaded = upload_date
            title_length = len(title)
            if len(title) > 300:
                title_length = 300
            title = title[:title_length]
            article_length = len(article)
            if len(article) > 6000:
                article_length = 6000
            article = article[:article_length]
            meta_length = len(meta)
            if len(meta) > 20:
                meta_length = 20
            company = meta[:meta_length]
            original_link = original
            seq_no = "{0:08d}".format(idx)
            content = (date.replace('-','')+seq_no, date, naver_link, original_link, sid, company, uploaded, title, article)
            cur.execute(query,content)
            conn.commit()
            sys.stdout.write("\rTotal: %d / %d" %(idx,len(link_list))),
            sys.stdout.flush()
            idx += 1
            driver.close()

        except Exception as e:
            if flag > 10:
                print(e)
                break
            else:
                flag+=1
                continue
        flag=0

    print("\nExecution time = {0:.5f}".format(time.time() - start))
    driver.quit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    date = sys.argv[1]
    main_start = time.time()
    #crawler('001',date)
    crawler('100',date)
    crawler('101',date)
    crawler('102',date)
    crawler('103',date)
    crawler('104',date)
    crawler('105',date)
    print("\nTotal :: Execution time = {0:.5f}".format(time.time() - main_start))
