__author__ = 'Frank Shen'

import requests
import re
import json
import random
import os
import time
from multiprocessing import Pool
from spider.user_agent_list import user_agent


def getHtmlText(url, headers, params):
    '''
        :param url:请求的url地址
        :param headers: 请求头
        :param  params: 参数
        :param proxies: 代理IP
        :return: html
    '''
    try:
        time.sleep(random.random())
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status
        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            return r.text
    except requests.ConnectionError as e:
        return None


def getCDList(page):
    url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?'
    headers = {
        'user-agent': random.choice(user_agent),
        'referer': 'https://y.qq.com/portal/playlist.html'
    }
    params = {
        'picmid': '1',
        'rnd': '0.18966091123822126',
        'g_tk': '5381',
        'jsonpCallback': 'getPlaylist',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'jsonp',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq',
        'needNewCode': '0',
        'categoryId': '10000000',
        'sortId': '5',
        'sin': '0',
        'ein': '29'
    }
    for i in range(228):
        params['sin'] = str(0+page*30)
        params['ein'] = str(29+page*30)
        html_content = getHtmlText(url, headers=headers, params=params)
        pattern = re.compile(r'^(\w+[(])(.*?)[)]$')
        item = re.findall(pattern, html_content)[0][1]
        dissid_content = json.loads(item)
        for diss in dissid_content['data']['list']:
            yield diss['dissid']


def getSongInfo(dissid):
    url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?'
    headers = {
        'user-agent': random.choice(user_agent),
        'referer': 'https://y.qq.com/n/yqq/playsquare/%s.html' % dissid
    }
    params = {
        'type': '1',
        'json': '1',
        'utf8': '1',
        'onlysong': '0',
        'disstid': dissid,
        'format': 'jsonp',
        'g_tk': '5381',
        'jsonpCallback': 'playlistinfoCallback',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'jsonp',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq',
        'needNewCode': '0'
    }
    html_content = getHtmlText(url, headers=headers, params=params)
    pattern = re.compile(r'^(\w+[(])(.*?)[)]$')
    data = re.findall(pattern, html_content)[0][1]
    song_content = json.loads(data)
    songlist = song_content['cdlist'][0]['songlist']
    dissname = song_content['cdlist'][0]['dissname']
    for song in songlist:
        yield{
            'dissname': dissname,
            'songname': song['songname'],
            'songmid': song['songmid'],
            'strMediaMid': song['strMediaMid']
        }


def getVkey(songmid):
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?'
    headers = {
        'referer': 'https://y.qq.com/portal/player.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    params = {
        'callback': 'getplaysongvkey23696929705391145',
        'g_tk': '5381',
        'jsonpCallback': 'getplaysongvkey23696929705391145',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'jsonp',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq',
        'needNewCode': '0',
        'data': '{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"1768216576","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"1768216576","songmid":["001o6b5J1d6D7G"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}},"comm":{"uin":0,"format":"json","ct":20,"cv":0}}'
    }
    pattern = re.compile('"songmid":.*?,')
    params['data'] = re.sub(pattern, '"songmid":["%s"],' % songmid, params['data'])
    html = requests.get(url, headers=headers, params=params).text
    pattern = re.compile('"vip_downfromtag":0,"vkey":"(.*?)"')
    vkey = re.findall(pattern, html)[0]
    return vkey


def download(strMediaMid, vkey, songname, dissname):
    path = 'd:\\data\\qqmusic\\歌单2\\'
    pattern = re.compile(r'[\\/:：*?"<>|\r\n]+')
    songname = re.sub(pattern, " ", songname)
    dissname = re.sub(pattern, " ", dissname)
    url = 'http://dl.stream.qqmusic.qq.com/C400%s.m4a?guid=1768216576&vkey=%s&uin=0&fromtag=66' % (
        strMediaMid, vkey)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        path = path + '%s\\' % dissname
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + '%s.m4a' % songname, 'wb') as f:
            print("正在下载:%s" % songname)
            f.write(r.content)


def main(page):
    for dissid in getCDList(page):
        for song in getSongInfo(dissid):
            songname = song['songname']
            songmid = song['songmid']
            strMediaMid = song['strMediaMid']
            dissname = song['dissname']
            vkey = getVkey(songmid)
            download(strMediaMid, vkey, songname, dissname)


if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i for i in range(1)])

