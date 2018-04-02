import re
import time
import sys
import os
import pymysql as psql
import sshtunnel
import datetime
import pandas as pd
def extractor(start_dt, end_dt):

    conn = psql.connect(host='localhost', db='************',user='**********', password='************', charset='utf8')
    query = """SELECT naver_link,original_link,sid,company,upload_date,title,text FROM news_total
               WHERE upload_date between %s and %s LIMIT %s OFFSET %s;"""
    query_count = """SELECT count(*) FROM news_total
                     WHERE upload_date between %s and %s;""" 
    cur = conn.cursor()
    cur.execute(query_count, (start_dt,end_dt))
    total = cur.fetchall()
    limit = 1000
    offset = 0

    news_list = []
    start = time.time()
    print("Total: {}".format(total[0][0]))
    while True:
        content = (start_dt, end_dt, limit, offset)
        cur.execute(query,content)
        records = cur.fetchall()
        offset += limit
        if records:
            news_list += records
        else:
            break
    print("\nExecution time = {0:.5f}".format(time.time() - start))
    cur.close()
    conn.close()
    return news_list

def search(keyword, start, end):
    key_news=[]
    start = datetime.datetime.strptime(start, '%Y-%m-%d') - datetime.timedelta(1)
    end =  datetime.datetime.strptime(end, '%Y-%m-%d') + datetime.timedelta(1)
    news_list = extractor(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    for news in news_list:
        if keyword in news[5] or keyword in news[6]:
            key_news.append(news)
    return key_news

if __name__ == '__main__':

    print(len(search('한국전자인증', '2018-01-15','2018-01-16')))
