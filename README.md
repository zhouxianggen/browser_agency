browser_agency
![](https://img.shields.io/badge/python%20-%203.7-brightgreen.svg)
========
> gov file crawler

## `Install`
```
pip install --upgrade -r requirements.txt
pip install git+https://github.com/zhouxianggen/browser_agency.git
```

## `Upgrade`
` pip install --upgrade git+https://github.com/zhouxianggen/browser_agency.git`

## `Uninstall`
` pip uninstall browser_agency`

## `Run`
` supervisorctl -c supervisord.conf restart browser_agency: `

## `Example`
```
import requests

url = 'https://m.1688.com/offer/564638707168.html?'
actions = [
        ('waitForXPath', ('//*[@id="widget-wap-detail-common-attribute"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
        ('keyboard.press', ('ArrowDown', {'delay': 250})),
        ('keyboard.press', ('ArrowDown', {'delay': 250})),
        ('waitForXPath', ('//*[@id="widget-wap-detail-common-preferential"]/div/div[1]', {'timeout': 10000, 'visible': 1})), 
        ('click', ('#J_WapCommonPreferenceList', )), 
        ]
actions = json.dumps(actions, ensure_ascii=False)

r = requests.post('http://host:port/_open', 
        data={'url': url, 'user-agency': '', 'actions': actions})
d = json.loads(r.content)
print(d['status'])
if d['status'] == 'OK':
    print(len(d['html']))

```
