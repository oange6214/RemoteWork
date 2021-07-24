import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

import pandas as pd
import random
import opencc
import json


class base_crawler:
    BASE_URL = 'https://cn.investing.com/instruments/HistoricalDataAjax'

    interval_sec = {
        'd': 'Daily',
        'w': 'Weekly',
        'm': 'Monthly'
    }

    headers = {
        'Host': 'cn.investing.com',
        'cookie': 'PHPSESSID=as00d2r39eeac12n7njjsavvdk; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A4%3A%226408%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A28%3A%22%2Fequities%2Fapple-computer-inc%22%3B%7D%7D%7D%7D; geoC=TW; adBlockerNewUserDomains=1627038453; StickySession=id.15597594000.601cn.investing.com; udid=fe19378ef8763ef135145c9c06510e5d; smd=fe19378ef8763ef135145c9c06510e5d-1627038453; __cflb=0H28uxmf5JNxjDUC6WDvQUEoJyvKUTrk7RmqgVt7wJt; protectedMedia=2; _ga=GA1.2.1750049023.1627038456; _gid=GA1.2.1565114425.1627038456; G_ENABLED_IDPS=google; adsFreeSalePopUp=3; logglytrackingsession=be89d5d2-a4b8-4804-9dc8-246878a1a212; __cf_bm=016e99075320f3dcc38a838de491171113a57738-1627047481-1800-AdzdcYWrxy8hCRHJK1XORozq9TcZRrZEoYDyOX5UeDKH20X2/KeqmJaiul40GC85sbryCIpNNxszUGeJEI2NeZLwDhGIQT9EZoT/hkORr9F3zewrbv4mmSt/SDNzw1Cjvw==; Hm_lvt_a1e3d50107c2a0e021d734fe76f85914=1627038457,1627047671; nyxDorf=OT0xamI2YSM%2Fa2hnMGZkeD9tN3JjZmVv; _gat=1; _gat_allSitesTracker=1; Hm_lpvt_a1e3d50107c2a0e021d734fe76f85914=1627047904; outbrain_cid_fetch=true; firstUdid=0',
        'origin': 'https://cn.investing.com',
        'referer': 'https://cn.investing.com/equities/apple-computer-inc-historical-data',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    proxy_list = [
        {"http": "220.184.144.80:8060"},
        {"http": "139.175.170.210:8060"},
        {"http": "116.226.57.17:8060"},
        {"http": "180.123.137.72:8060"},
        {"http": "116.226.31.161:8060"}
    ]

    def __init__(self, st_data, nd_data, interval_sec_type='d'):
        # 選擇起始、結束
        self.st_data = st_data
        self.nd_data = nd_data
        self.interval_sec_type = interval_sec_type

        self.from_data = {
            'curr_id': 6408,
            'smlID': 1159963,
            'header': 'AAPL历史数据',
            'st_date': st_data,
            'end_date': nd_data,
            'interval_sec': self.interval_sec[interval_sec_type],
            'sort_col': 'date',
            'sort_ord': 'DESC',
            'action': 'historical_data'
        }

    def set_base_url(self, base_url):
        if type(base_url) is str:
            self.BASE_URL = base_url
            return True
        return False

    def set_crawler_headers(self, headers):
        if type(headers) is type(dict()):
            self.headers = headers
            return True
        return False

    def get_crawler_headers(self):
        return self.headers

    def set_proxy_list(self, proxy):
        '''
            If proxy is the Type of dict Return True, otherwise Return False.

            Ex. {'html': '116.226.31.161:8060'}
        '''
        if type(proxy) is type(dict()):
            self.proxy_list.append(proxy)
            return True
        return False

    def get_proxy_list(self):
        return self.proxy_list

    def set_from_data(self, data):
        if type(data) is type(dict()):
            self.from_data = data
            return True
        return False

    def get_from_data(self):
        return self.from_data

    def paraser_html(self, html_path='output.html', encoding='gbk'):
        proxy      = random.choice(self.proxy_list)

        http_proxy_handler = urllib.request.ProxyHandler(proxy)
        opener             = urllib.request.build_opener(http_proxy_handler)

        data   = urllib.parse.urlencode(self.from_data).encode('ascii') # data should be bytes
        req    = urllib.request.Request(self.BASE_URL, data, headers=self.headers)
        res    = opener.open(req)
        result = res.read().decode()

        soup       = BeautifulSoup(result, 'lxml')
        prettyHTML = soup.prettify()

        with open(html_path, "w", encoding=encoding) as file:
            file.write(prettyHTML)

        return html_path

    def html_to_json(html_path, json_path='result.json', encoding='gbk'):
        def word_traditional_zh(data):
            op_cc = opencc.OpenCC('s2t')
            opc = op_cc.convert(data)
            return opc

        html = 'output.html'

        pd_data = pd.read_html(html, encoding='gbk')[0]
        pd_data.columns = [word_traditional_zh(d) for d in pd_data.columns]
        pd_data['日期'] = pd_data['日期'].apply(word_traditional_zh)

        pd_total = pd.read_html(html, encoding='gbk')[1]
        pd_total.iloc[0] = pd_total.iloc[0].apply(word_traditional_zh)

        js_data = pd_data.to_json(orient='table', index=False)
        js_total = pd_total.to_json(orient='table', index=False)

        dictA = json.loads(js_data)
        dictA['total'] = json.loads(js_total)

        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(dictA, json_file)

        return html_path

if __name__ == '__main__':
    # 參數 'Start Date', 'End Date', 'Inter
    base_crawler = base_crawler('2021/06/05', '2021/07/23')

    html = base_crawler.paraser_html('output.html')
    base_crawler.html_to_json(html, 'result.json')