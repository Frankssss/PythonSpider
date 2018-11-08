import requests
import random
import threading
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
from spider.user_agent_list import user_agent
from queue import Queue


class DBHandler(object):
    def __init__(self, dbName, table):
        self.host = "127.0.0.1"
        self.port = 27017
        self.dbName = dbName
        self.table = table
        self.client = MongoClient(host=self.host, port=self.port)
        self.tdb = self.client[self.dbName]
        self.post = self.tdb[self.table]

    def insert_data(self, data):
        self.post.insert(data)


class CrawlThread(threading.Thread):
    def __init__(self, name, page_queue, data_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.page_queue = page_queue
        self.data_queue = data_queue
        self.url = 'https://search.51job.com/list/020000,000000,0000,00,9,99,python,2,{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
        self.headers = {'user-agent': random.choice(user_agent)}

    def run(self):
        print('%s 开始' % self.name)
        while 1:
            if self.page_queue.empty():
                break
            page = self.page_queue.get()
            url = self.url.format(page)
            html = self.get_html_text(url, self.headers)
            self.data_queue.put(html)
        print('%s 结束' % self.name)

    @staticmethod
    def get_html_text(url, headers):
        try:
            r = requests.get(url, headers=headers)
            r.encoding = r.apparent_encoding
            r.raise_for_status()
            if r.status_code == 200:
                return r.text
        except:
            return None


class ParseThread(threading.Thread):
    def __init__(self, name, data_queue, db):
        super(ParseThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.db = db

    def run(self):
        print('%s 开始' % self.name)
        while 1:
            try:
                html = self.data_queue.get(True, 60)
            except:
                break
            for result in self.parse_data(html):
                print(result)
                self.db.insert_data(result)
        print('%s 结束' % self.name)

    @staticmethod
    def parse_data(html):
        soup = bs(html, 'lxml')
        table = soup.find('div', class_='dw_table')
        els = table.find_all('div', class_='el')
        for el in els[1:]:
            title = el.find('p').find('span').find('a').get('title')
            company = el.find('span', class_='t2').find('a').get('title')
            location = el.find('span', class_='t3').get_text()
            salary = el.find('span', class_='t4').get_text()
            publish_time = el.find('span', class_='t5').get_text()
            yield {
                  'title': title,
                  'company': company,
                  'location': location,
                  'salary': salary,
                  'publish_time': publish_time
            }


def create_crawl_thread(page_queue, data_queue):
    crawl_thread_list = []
    thread_name = ['爬取线程1', '爬取线程2', '爬取线程3']
    for name in thread_name:
        t = CrawlThread(name, page_queue, data_queue)
        crawl_thread_list.append(t)
    return crawl_thread_list


def create_parse_thread(data_queue, db):
    parse_thread_list = []
    thread_name = ['解析线程1', '解析线程2', '解析线程3']
    for name in thread_name:
        t = ParseThread(name, data_queue, db)
        parse_thread_list.append(t)
    return parse_thread_list


def create_queue():
    page_queue = Queue()
    data_queue = Queue()
    for i in range(1, 188):
        page_queue.put(i)
    return page_queue, data_queue


def main():
    db = DBHandler('Job', 'Test1')
    page_queue, data_queue = create_queue()
    crawl_thread_list = create_crawl_thread(page_queue, data_queue)
    parse_thread_list = create_parse_thread(data_queue, db)
    for t in crawl_thread_list:
        t.start()
    for t in parse_thread_list:
        t.start()
    for t in crawl_thread_list:
        t.join()
    for t in parse_thread_list:
        t.join()


if __name__ == '__main__':
    main()

