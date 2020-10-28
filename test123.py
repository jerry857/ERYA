import requests
import time
from bs4 import BeautifulSoup
import re
cookies = {
    'name': 'value',
    'Hm_lvt_7c382e68aaaa2864b0b7c79fc3554154': '1603634502',
    'JSESSIONID': '9C83F509D22062ACA86BBBF514EC22E0',
    'Hm_lpvt_7c382e68aaaa2864b0b7c79fc3554154': '1603683558',
}

headers = {
    'Host': 'www.livedu.com.cn',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://www.livedu.com.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.livedu.com.cn/ispace4.0/moocxsxx/queryAllZjByKcdm.do',
    'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
}
f=open("./content.html",encoding="utf-8")
last_resp=f.read()
f.close()
last_zjdm=re.search(r"zjdm = \"(.*?)\"",last_resp).group(0)
ZJDM=re.findall("xsxx\(\'.*?\'\)",last_resp)
for zjdm in ZJDM:
    zjdm=zjdm[6:10]
    try:
        zjdm=int(zjdm)
    except:
        continue
    if zjdm<=5515:
        continue
    bjdm=re.search("name=\"bjdm\" value=\"(.*?)\"",last_resp).group(1)
    url = "/ispace4.0/moocxsxx/checkSfxx.do"
    kcdm="216"
    param = {'kcdm': kcdm, 'zjdm': zjdm}
    check= requests.post('https://www.livedu.com.cn/ispace4.0/moocxsxx/checkSfxx.do', headers=headers,
                             cookies=cookies, data=param).text

    data = {
        'kcdm': '216',
        'zjdm': zjdm,  # +zj,
        'bjdm': bjdm,
        "sftj":"0",
        "sfShowStjc":"",
        "styflag":"1",
        "res":"",
    }
    last_resp = requests.post('https://www.livedu.com.cn/ispace4.0/moocxsxx/queryAllZjByKcdm.do', headers=headers,
                             cookies=cookies, data=data).text

    streamName=re.search("onended=\"myFunction\(\'(.*?)\'",last_resp).group(1)
    index = streamName.index("/")
    streamName = streamName[index + 1:]
    data = {
      'kcdm': '216',
      'zjdm': zjdm,#+zj,
      'streamName': streamName
    }
    resp_ = requests.post('https://www.livedu.com.cn/ispace4.0/moocxsxx/updKcspSqzt.do', headers=headers, cookies=cookies, data=data)

    print(zjdm,resp_.text)
    time.sleep(800)
if __name__ == '__main__':
    pass