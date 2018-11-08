import requests
import random
import json
import time
import threading
from queue import Queue


class CrawlThread(threading.Thread):
    def __init__(self, name, page_queue, data_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.page_queue = page_queue
        self.data_queue = data_queue
        self.url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'

    def run(self):
        print('%s 开始' % self.name)
        while 1:
            if self.page_queue.empty():
                break
            page = self.page_queue.get()
            json_data = CrawlThread.getHtmlText(self.url, page)
            self.data_queue.put(json_data)
        print('%s 结束' % self.name)

    @staticmethod
    def getHtmlText(url, page):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Cookie': 'WEBTJ-ID=20181105221518-166e43a4f0b5de-0d214181c7b63c-b79183d-1327104-166e43a4f0c2e; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539522718,1539688198,1541427319; _ga=GA1.2.1583729187.1541427319; _gid=GA1.2.1114343443.1541427319; user_trace_token=20181105221513-3633181a-e105-11e8-8693-5254005c3644; LGSID=20181105221513-36331ad0-e105-11e8-8693-5254005c3644; PRE_UTM=m_cf_cpt_baidu_pc; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Fs%3Fie%3Dutf-8%26f%3D8%26rsv_bp%3D0%26rsv_idx%3D1%26tn%3Dbaidu%26wd%3D%25E6%258B%2589%25E5%258B%25BE%25E7%25BD%2591%26rsv_pq%3D87b41c6b0002722b%26rsv_t%3D2748kGQ%252Frq2Px4PF7pY6SH2FZjdInSrspkmlHMCvqbrmLXTpQjyt4dMtSgI%26rqlang%3Dcn%26rsv_enter%3D1%26rsv_sug3%3D11%26rsv_sug1%3D7%26rsv_sug7%3D101%26rsv_sug2%3D0%26inputT%3D1080%26rsv_sug4%3D1803%26rsv_sug%3D1; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Flp%2Fhtml%2Fcommon.html%3Futm_source%3Dm_cf_cpt_baidu_pc; LGUID=20181105221513-36331cc9-e105-11e8-8693-5254005c3644; X_HTTP_TOKEN=52b20079803d19a4de523e90123d6bb5; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22166e43a5d99782-00df88156a85bb-b79183d-1327104-166e43a5d9a3aa%22%2C%22%24device_id%22%3A%22166e43a5d99782-00df88156a85bb-b79183d-1327104-166e43a5d9a3aa%22%2C%22props%22%3A%7B%22%24latest_utm_source%22%3A%22m_cf_cpt_baidu_pc%22%7D%7D; LG_LOGIN_USER_ID=67f7a7b88b45dba8c7be6380dc1370b9e32ad57812814a4233a3d6175a90bc27; _putrc=BA1BDB49F9433782123F89F2B170EADC; JSESSIONID=ABAAABAABEEAAJAC263F91FAC22C78D15FC305E9DACC61A; login=true; unick=%E6%B2%88%E8%BE%89; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; gate_login_token=b836dce431ff6fc44234b57136fea24fe0dfc7992fb9bc3a067061d15bb8e6ca; index_location_city=%E5%85%A8%E5%9B%BD; _gat=1; TG-TRACK-CODE=search_code; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1541427590; LGRID=20181105221944-d7ab5466-e105-11e8-8693-5254005c3644; SEARCH_ID=808548e8b0754b00a63f9cf7ed4750ac',
            'Referer': 'https://www.lagou.com/jobs/list_python%E7%88%AC%E8%99%AB?oquery=Python&fromSearch=true&labelWords=relative'
        }
        post_data = {
            'first': 'false',
            'pn': '',
            'kd': 'python爬虫',
        }
        post_data['pn'] = str(page)
        try:
            time.sleep(random.random())
            r = requests.post(url, headers=headers, data=post_data)
            r.raise_for_status()
            if r.status_code == 200:
                return r.json()
        except:
            print('html异常')


class ParseThread(threading.Thread):
    def __init__(self, name, data_queue, lock):
        super(ParseThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.lock = lock

    def run(self):
        print('%s 开始' % self.name)
        while 1:
            try:
                json_data = self.data_queue.get(True, 5)
            except:
                break
            items = json_data['content']['positionResult']['result']
            data = self.parseData(items)
            self.lock.acquire()
            ParseThread.write_to_file(data)
            self.lock.release()
        print('%s 结束' % self.name)

    def parseData(self, items):
        data = []
        for item in items:
            education = item['education']
            jobNature = item['jobNature']
            positionName = item['positionName']
            workYear = item['workYear']
            salary = item['salary']
            city = item['city']
            financeStage = item['financeStage']
            industryField = item['industryField']
            createTime = item['createTime']
            positionAdvantage = item['positionAdvantage']
            companyShortName = item['companyShortName']
            companySize = item['companySize']
            companyLabelList = item['companyLabelList']
            district = item['district']
            positionLabels = item['positionLables']
            companyFullName = item['companyFullName']
            firstType = item['firstType']
            secondType = item['secondType']
            linestaion = item['linestaion']
            thirdType = item['thirdType']
            skillLabels = item['skillLables']
            data.append([education, jobNature, positionName, workYear, salary, city, financeStage,
                         industryField, createTime, positionAdvantage, companyShortName, companySize,
                         companyLabelList, district, positionLabels, companyFullName, firstType,
                         secondType, linestaion, thirdType, skillLabels])
            print([education, jobNature, positionName, workYear, salary, city, financeStage,
                 industryField, createTime, positionAdvantage, companyShortName, companySize,
                 companyLabelList, district, positionLabels, companyFullName, firstType,
                 secondType, linestaion, thirdType, skillLabels])
        return data

    @staticmethod
    def write_to_file(data):
        with open('lagou_python爬虫.txt', 'a', encoding='utf8') as f:
            for i in data:
                f.write(json.dumps(i, ensure_ascii=False) + '\n')


def create_queue():
    page_queue = Queue()
    for i in range(1, 26):
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


def create_parse_thread(data_queue, lock):
    threads = []
    thread_name = ['解析线程1', '解析线程2', '解析线程3']
    for name in thread_name:
        t = ParseThread(name, data_queue, lock)
        threads.append(t)
    return threads


def main():
    lock = threading.Lock()
    page_queue, data_queue = create_queue()
    crawl_threads = create_crawl_thread(page_queue, data_queue)
    parse_threads = create_parse_thread(data_queue, lock)
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