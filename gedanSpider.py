__author__ = 'Frank Shen'

'''
爬取QQ音乐歌单

1.通过分析歌曲下载路径来分析所需参数： 通过比较， 得出其中歌曲下载url 与参数 vkey 是可变的，
歌曲下载url中可变得值是请求歌单返回的歌曲数据的strMediaMid参数, 而vkey是通过请求歌单返回的歌曲数据的songmid参数再次请求另一个url返回vkey值
2.通过分析请求歌单url来分析所需参数: dissid  
dissid为请求diss的返回数据中的dissid参数

'''
import os
import re
import requests
from urllib.parse import urlencode
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'origin': 'https://y.qq.com',
    'referer': 'https://y.qq.com/portal/playlist.html'
}


def fetch_url(url):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code in [200, 201]:
            return r.json()
    except Exception as e:
        print(e)


def down_song(path, strMediaMid, vkey):
    params = {
        'guid': '5300386295',
        'vkey': vkey,
        'uin': '0',
        'fromtag': '66'
    }
    url = 'http://222.73.132.154/amobile.music.tc.qq.com/C400{}.m4a?'.format(strMediaMid)
    url += urlencode(params)
    r = requests.get(url, headers=headers)
    if r.status_code in [200, 201]:
        with open(path, 'wb') as f:
            f.write(r.content)


def get_vkey(songmid):
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?'
    params = {
        '-': 'getplaysongvkey7256617694143965',
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
        'data': '{"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"5300386295","songmid":["%s"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}},"comm":{"uin":0,"format":"json","ct":24,"cv":0}}' % songmid
    }
    url += urlencode(params)
    result = fetch_url(url)
    vkey = result['req_0']['data']['midurlinfo'][0]['vkey']
    return vkey


def get_song_info(disstid):
    url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?'
    params = {
        'type': '1',
        'json': '1',
        'utf8': '1',
        'onlysong': '0',
        'disstid': disstid,
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
    }
    url += urlencode(params)
    result = fetch_url(url)
    songlist = result['cdlist'][0]['songlist']
    for song in songlist:
        strMediaMid = song['strMediaMid']
        songMid = song['songmid']
        songname = song['songname']
        yield strMediaMid, songMid, songname


def get_dist_info(page):
    url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?'
    params = {
        'picmid': '1',
        'rnd': '0.15993662911508766',
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
        'categoryId': '10000000',
        'sortId': '5',
        'sin': int(page)*30-30,
        'ein': int(page)*30-1,
    }
    url += urlencode(params)
    result = fetch_url(url)
    disslist = result['data']['list']
    for diss in disslist:
        yield diss['dissid'], diss['dissname']


def main(page):
    for item in get_dist_info(page):
        dissid, dissname = item
        for item in get_song_info(dissid):
            strMediaMid, songMid, songname = item
            vkey = get_vkey(songMid)
            pattern = re.compile(r'[\\/:：*?"<>|\r\n]+')
            songname = re.sub(pattern, " ", songname)
            dissname = re.sub(pattern, " ", dissname)
            if not os.path.exists('d://data/{}/'.format(dissname)):
                os.mkdir('d://data/{}/'.format(dissname))
            path = 'd://data/{0}/{1}.m4a'.format(dissname, songname)
            print("正在下载：{}".format(songname))
            down_song(path, strMediaMid, vkey)
            print("下载完成：{}".format(songname))


if __name__ == '__main__':
    page = 1
    main(page)