__author__ = 'Frank Shen'

import csv
import requests
import random
import time
import threading
from queue import Queue
from spider.user_agent_list import user_agent
from bs4 import BeautifulSoup as bs


class CrawlThread(threading.Thread):
    def __init__(self, name, page_queue, data_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.page_queue = page_queue
        self.data_queue = data_queue
        self.url = 'http://www.81835.com/_house_dir.asp?typeto=1&Page={}'

    def run(self):
        print('%s 开始' % self.name)
        while 1:
            if self.page_queue.empty():
                break
            page = self.page_queue.get()
            url = self.url.format(page)
            html = CrawlThread.getHtmlText(url)
            self.data_queue.put(html)
        print('%s 结束' % self.name)

    @staticmethod
    def getHtmlText(url):
        try:
            headers = {'user-agent': random.choice(user_agent)}
            r = requests.get(url, headers=headers)
            r.encoding = r.apparent_encoding
            r.raise_for_status()
            if r.status_code == 200:
                return r.text
        except:
            print('html异常')


class ParseThread(threading.Thread):
    def __init__(self, name, data_queue, lock, f):
        super(ParseThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.lock = lock
        self.f = f

    def run(self):
        print('%s 开始' % self.name)
        while 1:
            try:
                html = self.data_queue.get(True, 10)
            except:
                break
            result = ParseThread.parseData(html)
            self.lock.acquire()
            self.f.writerows(result)
            self.lock.release()
        print('%s 结束' % self.name)

    @staticmethod
    def parseData(html):
        soup = bs(html, 'lxml')
        trs = soup.find_all('tr', attrs={'bgcolor': {'#f7f7f7', '#FFfFFF'}})
        for tr in trs:
            tds = tr.find_all('td')
            result = []
            for td in tds[:-1]:
                if 'div' in td:
                    text = td.find('div').get_text().strip('\n').strip(' \r\n            \xa0')
                else:
                    text = td.get_text().strip('\n').strip(' \r\n            \xa0')
                result.append(text)
            yield result


def create_queue():
    page_queue = Queue()
    for i in range(1, 801):
        page_queue.put(i)
    data_queue = Queue()
    return page_queue, data_queue


def create_crawl_thread(page_queue, data_queue):
    threads = []
    thread_name = ['爬取线程1', '爬取线程2', '爬取线程3']
    for name in thread_name:
        t = CrawlThread(name, page_queue, data_queue)
        threads.append(t)
    return threads


def create_parse_thread(data_queue, lock, f):
    threads = []
    thread_name = ['解析线程1', '解析线程2', '解析线程3']
    for name in thread_name:
        t = ParseThread(name, data_queue, lock, f)
        threads.append(t)
    return threads


def main():
    lock = threading.Lock()
    page_queue, data_queue = create_queue()
    with open('崇明房产信息.csv', 'a', encoding='utf-8-sig', newline='') as csvfile:
        f = csv.writer(csvfile)
        crawl_threads = create_crawl_thread(page_queue, data_queue)
        parse_threads = create_parse_thread(data_queue, lock, f)
        for thread in crawl_threads:
            thread.start()
        for thread in parse_threads:
            thread.start()
        for thread in crawl_threads:
            thread.join()
        for thread in parse_threads:
            thread.join()


if __name__ == '__main__':
    temp = time.time()
    main()
    print(time.time()-temp)
