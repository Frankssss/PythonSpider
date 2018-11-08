__author__ = 'Frank Shen'

import requests
import random
import time
from pymongo import MongoClient
from multiprocessing import Pool
from spider.user_agent_list import user_agent


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


def get_user_id():
    user_id_list = []
    url = 'https://500px.me/community/user-details/userInfos?page={}&size=20&type=json'
    for i in range(1, 51):
        url = url.format(i)
        headers = {'user-agent': random.choice(user_agent),}
        json_data = requests.get(url, headers=headers).json()
        for item in json_data:
            user_id = item['id']
            user_id_list.append(user_id)
    return user_id_list


def get_user_info(user_id):
    url = 'https://500px.me/community/v2/user/indexInfo?queriedUserId={}'.format(user_id)
    headers = {'user-agent': random.choice(user_agent), }
    json_data = requests.get(url, headers=headers).json()
    data = json_data['data']
    city = data['city']
    if 'coutry' in data:
        country = data['coutry']
    else:
        country = ''
    nickName = data['nickName']
    if 'province' in data:
        province = data['province']
    else:
        province = ''
    about = data['about']
    userPvedCount = data['userPvedCount']
    userFollowedCount = data['userFollowedCount']
    userFolloweeCount = data['userFolloweeCount']
    yield {
        'city': city,
        'country': country,
        'nickName': nickName,
        'province': province,
        'about': about,
        'userPvedCount': userPvedCount,
        'userFollowedCount': userFollowedCount,
        'userFolloweeCount': userFolloweeCount
    }


def main(user_id):
    db = DBHandler('Photographer', 'Test1')
    for result in get_user_info(user_id):
        db.insert_data(result)


if __name__ == '__main__':
    temp = time.time()
    user_id_list = get_user_id()
    pool = Pool(3)
    pool.map(main, user_id_list)
    pool.close()
    pool.join()
    print(time.time()-temp)