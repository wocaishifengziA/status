from enum import IntEnum
from urllib import parse

import requests
from lxml import etree

# from urllib.parse import urljoin
# headers = {
#     "Accept-Encoding": "zh-CN,zh;q=0.9",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
# }
# response = requests.get(url='http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/14.html', headers=headers)
# response.encoding = 'gb2312'
# html = etree.HTML(response.text)
#
# citys = html.xpath('//tr[@class="citytr"]/td[2]/a')
#
# for city in citys:
#     province_url = city.xpath('./@href')[0]
#     city_name = city.xpath('./text()')[0]
#     province_url = parse.urljoin(response.url, province_url)
#     print(province_url)

# class Level(IntEnum):
#     province = '2',
#     city = 3,
#     county = 4,
#     town = 5,
#     village = 6
#
# print(Level['province'].value)

# list_a = [1, 2, 3]
# list_a = tuple(list_a)
# list_a = tuple(list_a)
# print(list_a)
list_dict = []
dict = {'old':'test'}
list = [{'a': 11, 'b': 12, 'c': 13}, {'a': 21, 'b': 22, 'c': 23}, {'a': 31, 'b': 32, 'c': 33}]
for l in list:
    dict['a'] = l['a']
    dict['b'] = l['b']
    dict['c'] = l['c']

    dict_c = dict.copy()
    list_dict.append(dict_c)
print(list_dict)

