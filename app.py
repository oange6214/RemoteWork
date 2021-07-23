import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

import pandas as pd
import random
import opencc
import json

BASE_URL = 'https://cn.investing.com/instruments/HistoricalDataAjax'

headers  = {
    'Host': 'cn.investing.com',
    'cookie': 'PHPSESSID=as00d2r39eeac12n7njjsavvdk; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A4%3A%226408%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A28%3A%22%2Fequities%2Fapple-computer-inc%22%3B%7D%7D%7D%7D; geoC=TW; adBlockerNewUserDomains=1627038453; StickySession=id.15597594000.601cn.investing.com; udid=fe19378ef8763ef135145c9c06510e5d; smd=fe19378ef8763ef135145c9c06510e5d-1627038453; __cflb=0H28uxmf5JNxjDUC6WDvQUEoJyvKUTrk7RmqgVt7wJt; protectedMedia=2; _ga=GA1.2.1750049023.1627038456; _gid=GA1.2.1565114425.1627038456; G_ENABLED_IDPS=google; adsFreeSalePopUp=3; logglytrackingsession=be89d5d2-a4b8-4804-9dc8-246878a1a212; __cf_bm=016e99075320f3dcc38a838de491171113a57738-1627047481-1800-AdzdcYWrxy8hCRHJK1XORozq9TcZRrZEoYDyOX5UeDKH20X2/KeqmJaiul40GC85sbryCIpNNxszUGeJEI2NeZLwDhGIQT9EZoT/hkORr9F3zewrbv4mmSt/SDNzw1Cjvw==; Hm_lvt_a1e3d50107c2a0e021d734fe76f85914=1627038457,1627047671; nyxDorf=OT0xamI2YSM%2Fa2hnMGZkeD9tN3JjZmVv; _gat=1; _gat_allSitesTracker=1; Hm_lpvt_a1e3d50107c2a0e021d734fe76f85914=1627047904; outbrain_cid_fetch=true; firstUdid=0',
    'origin': 'https://cn.investing.com',
    'referer': 'https://cn.investing.com/equities/apple-computer-inc-historical-data',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

interval_sec = {
    'd': 'Daily',
    'w': 'Weekly',
    'm': 'Monthly'
}

# 選擇起始、結束
st_data  = '2021/06/05'
end_data = '2021/07/23'

from_data = {
    'curr_id': 6408,
    'smlID': 1159963,
    'header': 'AAPL历史数据',
    'st_date': st_data,
    'end_date': end_data,
    'interval_sec': interval_sec['d'],
    'sort_col': 'date',
    'sort_ord': 'DESC',
    'action': 'historical_data'
}

proxy_list = [
    {"http": "220.184.144.80:8060"},
    {"http": "139.175.170.210:8060"},
    {"http": "116.226.57.17:8060"},
    {"http": "180.123.137.72:8060"},
    {"http": "116.226.31.161:8060"}
]

def paraser_html(html_path='output.html', encoding='gbk'):
    proxy      = random.choice(proxy_list)

    http_proxy_handler = urllib.request.ProxyHandler(proxy)
    opener             = urllib.request.build_opener(http_proxy_handler)

    data   = urllib.parse.urlencode(from_data).encode('ascii') # data should be bytes
    req    = urllib.request.Request(BASE_URL, data, headers=headers)
    res    = opener.open(req)
    result = res.read().decode()

    soup       = BeautifulSoup(result, 'lxml')
    prettyHTML = soup.prettify()

    with open(html_path, "w", encoding=encoding) as file:
        file.write(prettyHTML)

    return html_path

def html_to_json(html_path, json_path='result.json', encoding='gbk'):
    def word_traditional_zh(data, tra_type='s2t'):
        op_cc = opencc.OpenCC(tra_type)
        opc = op_cc.convert(data)
        return opc

    pd_data = pd.read_html(html_path, encoding=encoding)[0]

    col_list = []
    for col in pd_data.columns:
        col_list.append(word_traditional_zh(col))
    pd_data.columns = col_list

    for date in pd_data['日期']:
        pd_data['日期'] = word_traditional_zh(date)

    pd_total = pd.read_html(html_path, encoding=encoding)[1]

    for total in pd_total.columns:
        pd_total[total][0] = word_traditional_zh(pd_total[total][0])

    js_data = pd_data.to_json(orient='table')
    js_total = pd_total.to_json(orient='table')

    dictA = json.loads(js_data)
    dictA['total'] = json.loads(js_total)

    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(dictA, json_file)

    return html_path

if __name__ == '__main__':
    html = paraser_html('output.html')
    html_to_json(html, 'result.json')