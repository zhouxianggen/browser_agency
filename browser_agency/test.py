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
url = 'https://m.1688.com/offer/564638707168.html?'
url = 'https://m.1688.com/offer/1198767727.html?'
url = 'https://m.1688.com/offer/564638707168.html?'
#url = sys.argv[1]

actions = [
        ('waitForXPath', ('//*[@id="widget-wap-detail-common-attribute"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
        ('keyboard.press', ('ArrowDown', {'delay': 250})),
        ('keyboard.press', ('ArrowDown', {'delay': 250})),
        ('waitForXPath', ('//*[@id="widget-wap-detail-common-preferential"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
        ('click', ('#J_WapCommonPreferenceList', )), 
        ]
actions = json.dumps(actions, ensure_ascii=False)

def foo(order=1):
    time.sleep(random.randint(1, 1000)/1000.)
    log.info('foo start')
    url2 = '{}#{}'.format(url, order)
    r = requests.post('http://localhost:8005/_open', 
            data={'url': url2, 'actions': actions})
    d = json.loads(r.content)
    log.info('foo end [{}:{}:{}]'.format(d['status'], d.get('error_code', ''), d.get('error_desc', '')))
    #if d['status'] == 'OK' or d.get('error_code', '') == 'ACTION_FAILED':
    #    open('/data/share/x.html', 'wb').write(d['html'].encode('utf8'))

foo()
sys.exit()

ts = [Thread(target=foo, args=(i,)) for i in range(5)]

for t in ts:
    t.start()

for t in ts:
    t.join()
log.info('wait ..')
