import pdb
import datetime as dt
import requests
import re
import json
import pandas as pd

from dateutil.relativedelta import relativedelta

from bs4 import BeautifulSoup
from config import *

def fetch_news_list(datestr, page):
    url = 'https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101&date={}&page={}'.format(
        datestr, page
    ) 

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }  # 사용하고 있는 브라우저 정보...--> 사람인척하는거. 사람인척 안하면 거부함. 기계가 보낸걸로 알고

    resp = requests.get(url, headers=headers)

    assert resp.status_code == 200   # status_code가 200인지 확인해라. 확인하고 아니면 멈춰라

    soup = BeautifulSoup(resp.text, 'html.parser')
    list_body = soup.find("div", {"class":"list_body"})

    buffer = []

    for item in list_body.find_all("li"):
        link = item.find_all('a')[-1]
        title = link.text.strip()
        publisher = item.find("span", {"class": "writing"}).text

        created_at = item.find("span", {"class":"date"}).text
        created_at = created_at.replace("오전", "AM").replace("오후", "PM")        
        created_at = dt.datetime.strptime(created_at, '%Y.%m.%d. %p %I:%M') # strf - string format ,    # strp - string parsing
        

        href = link['href']
        
        # print(title)
        # print(publisher)
        # print(created_at)
        # print(href)
        
        matched = re.search(r'mnews/article/(\d+)/(\d+)', href)  #괄호 사용시 나중에 뽑아낼 수 있다

        oid = matched[1]
        aid = matched[2]

        message_id = 'nn-{}-{}'.format(oid, aid)

        info = {
            'id' : message_id,
            'title' : title,
            'section' : 'economy',
            'publisher': publisher,
            'created_at': created_at.isoformat(),
            'url': href
        }

        buffer.append(info)
    
    return buffer        
        

def fetch_news_list_for_date(date):    
    datestr = date.strftime('%Y%m%d')      # str - string, f - format,   # %Y: 년도를 4자리로 쓰는거, %m: 

    print('[{}] Fetching news list on {}...'.format(
        dt.datetime.now(), datestr
        ))

    prev_last_id = None

    queue = []

    for page in range(1, 10):
    # for page in range(1, 1000):
        print('Fetching page {}...'.format(page))

        buffer = fetch_news_list(datestr, page)

        if buffer[-1]['id'] == prev_last_id:
            break
        else:
            prev_last_id = buffer[-1]['id']

        
        # upload_to_elastic_search(buffer)
        queue += buffer

        if len(buffer) < 20:
            break
    
    save_to_excel(datestr, queue)

def save_to_excel(datestr, queue):
    df = pd.DataFrame(queue)

    filename = 'naver-news-{}.xlsx'.format(datestr)

    df.to_excel(filename)

    df.to_excel(filename)


    pdb.set_trace()


def upload_to_elastic_search(buffer):
    if len(buffer) == 0:
        return
    
    data = ''

    for x in buffer:
        index = {
            'index': {
                '_id': x['id']
            }
        }

        data += json.dumps(index) + '\n'
        data += json.dumps(x) + '\n'

    headers = {
        'Content-Type': 'application/json'
    }

    resp = requests.post(
        f'{ELASTCSEARCH_URL}/news/_bulk?pretty&refresh',
        headers = headers,
        data = data,
        auth = ELASTCSEARCH_AUTH,
    )
    
    assert resp.status_code == 200


if __name__=='__main__':
    base_date = dt.datetime(2022, 8, 1)

    for d in range(10):
        date = base_date + relativedelta(days=d)  # days: 추가를 해라, day: 해당 날짜로 바꿔라
        
        fetch_news_list_for_date(date)
        
    