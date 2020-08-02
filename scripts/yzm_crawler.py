import os
import time

import requests

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'


def crawler(_url, _ua, sleeptime=1, limit=5, storedir="./"):
    cookies = {
        "JSESSIONID": "0001dDIP581SwEuxLCfJF8aKPmJ:58KFNQ6PO"
    }
    try:
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass
    print("All contents will be downloaded to " + storedir)
    for i in range(0, limit):
        s = requests.session()
        req = s.get(url=_url, headers=_ua, verify=False, cookies=cookies)
        if req.status_code == requests.codes.OK:
            name = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
            if not os.path.exists(storedir):
                os.makedirs(storedir)
            f = open(storedir + name + '.jpg', 'wb')
            f.write(req.content)
            f.close()
            print("downloaded:", i)
            print("left:", limit - i)
            if i % 5 == 0 and i != 0:
                print("------------")
                time.sleep(5)
            else:
                print("------------")
                time.sleep(sleeptime)
    print("download success")


url = 'https://jwxt.bupt.edu.cn/validateCodeAction.do'

ua = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Referer': 'jwxt.bupt.edu.cn'
}
crawler(url, ua, storedir="./yzm/source/", limit=5)
