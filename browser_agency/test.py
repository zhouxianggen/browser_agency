# coding: utf8
import os
import sys
import time
import random
import json
from threading import Thread
import requests
from pyutil import get_logger


log = get_logger()
#host = 'http://101.37.223.149/_open'
host = 'http://localhost:7777/_open'
url = 'https://m.1688.com/offer/564638707168.html?'
url = 'https://m.1688.com/offer/1198767727.html?'
url = 'https://m.1688.com/offer/564638707168.html?'
if len(sys.argv) > 1:
    url = sys.argv[1]

def test1():
    url = 'https://m.1688.com/offer/564638707168.html?'
    actions = [
            ('waitForXPath', ('//*[@id="widget-wap-detail-common-attribute"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
            ('keyboard.press', ('ArrowDown', {'delay': 250})),
            ('keyboard.press', ('ArrowDown', {'delay': 250})),
            ('waitForXPath', ('//*[@id="widget-wap-detail-common-preferential"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
            ('click', ('#J_WapCommonPreferenceList', )), 
            ]
    actions = json.dumps(actions, ensure_ascii=False)
    r = requests.post(host, 
            data={'url': url, 'actions': actions})
    d = json.loads(r.content)
    log.info('foo end [{}:{}:{}]'.format(d['status'], d.get('error_code', ''), d.get('index', '')))
    if d.get('html'):
        open('/data/share/x.html', 'wb').write(d['html'].encode('utf8'))


def test2():
    url = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=%E9%82%B5%E4%B8%9C&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=983&sst0=1553847032923&lkt=0%2C0%2C0'
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    actions = [
            ]
    actions = json.dumps(actions, ensure_ascii=False)
    r = requests.post(host, 
            data={'url': url, 'User-Agent':UA, 'actions': actions})
    d = json.loads(r.content)
    log.info('foo end [{}:{}:{}]'.format(d['status'], d.get('error_code', ''), d.get('index', '')))
    if d.get('html'):
        open('/data/share/x.html', 'wb').write(d['html'].encode('utf8'))

test2()

