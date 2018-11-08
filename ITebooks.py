__author__ = 'Frank Shen'

import requests
import random
import time
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
from spider.user_agent_list import user_agent
headers = {'user-agent': random.choice(user_agent), }


def get_book_link():
    url = 'http://www.allitebooks.com/page/{}/'
    for i in range(1, 11):
        url = url.format(i)
        html = requests.get(url, headers=headers).text
        soup = bs(html, 'lxml')
        div = soup.find('div', class_='main-content-inner clearfix')
        articles = div.find_all('article')
        for article in articles:
            book_link = article.find('div', class_='entry-body').find('h2', class_='entry-title').find('a').get('href')
            yield book_link


def get_book_address(book_link):
    html = requests.get(book_link, headers=headers).text
    soup = bs(html, 'lxml')
    address = soup.find('span', class_='download-links').find('a').get('href')
    yield address


def book_download(address):
    title = address.rsplit('/', 1)[1]
    r = requests.get(address, headers=headers)
    with open('d:\\data\\ebooks\\%s' % title, 'wb') as f:
        f.write(r.content)


def main(book_link):
    for address in get_book_address(book_link):
        book_download(address)


if __name__ == '__main__':
    temp = time.time()
    pool = Pool(3)
    pool.map(main, [i for i in get_book_link()])
    pool.close()
    pool.join()
    print(time.time()-temp)