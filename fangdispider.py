__author__ = 'Frank Shen'

import requests
import time
import json
import pandas as pd
from bs4 import BeautifulSoup as bs
import threading
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Cookie': 'FSSBBIl1UgzbN7N7001S=d0VxfW2uWGeStwF6wQZIo9iGTUlm2raz_dQb3Va8A41GWB1k7zA1oydzlCqnP0s6; FSSBBIl1UgzbN7N7001T=3kMBVBxh5yAVHSXMMJvUXAlcU48DwDckef6PmJM4gsglBSkhd1ifXJARVgXFiOYsmoHpV0Y.fWbajfq1FSMgHUgM.v.JzgvzpxOdhM5aNx9PH9uXNGUIfPvGItEa9vHwaGfe2_5j1o3N6YapYCEbYjgDjoAtTmxAHXTkTATPXVWZXMQv88DGopTFrBLufmskFgBXBeGy0UNeaRmqT9d5ATpIVHjOvcu_ml73KlffiyS1_ZWLawnGYN3_qwHHR0RLTuZbHYl5K6Brw.pGZ6IZn_5wxGhdQiOdgz1K.LTb1FkIi6z7IkOYezFpGnVeFlNH3EKTixD_nH2AkZsf9Ihpi.z0W; JSESSIONID1=E83n3Mo3zZ1usv_Tho6kg6dP-pWVsQFOUXQrwtwy6fODxl54g4_g!404224306',
        'Host': 'www.fangdi.com.cn',
        'Origin': 'http://www.fangdi.com.cn',
        'Referer': 'http://www.fangdi.com.cn/old_house/old_house_list.html?district=27d3af3bd45acf5e&area=&location=&listingNo=&region=&price=&blockName=&time=&houseType=&check_input=ZCV8',
    }


def getDicList(url, headers):
    json_data = requests.get(url, headers=headers).json()
    dicList = json_data['dicList']
    for dic in dicList:
        yield [dic['name'], dic['code']]


def getHouseInfo(headers, value):
    url = 'http://www.fangdi.com.cn/oldhouse/selectOldHouse.action'
    page = 1
    data = {
        'district': value,
        'area': '',
        'location': '',
        'price': '',
        'region': '',
        'blockName': '',
        'time': '',
        'houseType': '',
        'listingNo': '',
        'currentPage': '',
    }
    result = []
    while 1:
        data['currentPage'] = str(page)
        r = requests.post(url, headers=headers, data=data)
        json_data = json.loads(r.text)
        table = json_data['htmlView']
        soup = bs(table, 'lxml')
        total_page = soup.find('span', class_='page_total').find('i').get_text()
        if page > int(total_page):
            break
        trs = soup.find_all('tr')[1:]
        for tr in trs:
            tds = tr.find_all('td')
            temp = []
            for td in tds[:-1]:
                temp.append(td.get_text())
            result.append(temp)
        page += 1
    yield result


def main(item):
    print('%s 正在存储' % item[0])
    for result in getHouseInfo(headers, item[1]):
        data = pd.DataFrame(result)
        data.to_excel(item[2], sheet_name='%s' % item[0], encoding='utf_8_sig', index=False, header=['区域', '位置', '房型', '朝向', '楼层', '面积（平方米）', '总价（元）'])
    print('%s 存储完毕' % item[0])


if __name__ == '__main__':
    temp = time.time()
    url = 'http://www.fangdi.com.cn/oldhouse/getDic.action'
    threads = []
    writer = pd.ExcelWriter('二手房.xlsx')
    for item in getDicList(url, headers):
        t = threading.Thread(target=main, args=([item[0], item[1], writer],))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    writer.close()
    print(time.time()-temp)