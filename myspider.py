from enum import IntEnum
from urllib import parse
import requests
import pymysql
from lxml import etree
# 增加 mysql 多条插入

class Level(IntEnum):
    province = 2,
    city = 3,
    county = 4,
    town = 5,
    village = 6

BASE_URL = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html'
TABLE = 'jkl'
# mysqlhost = '47.92.27.98'
mysqlhost = '127.0.0.1'
class StatusSpider(object):

    def __init__(self):
        self.headers = {
            "Accept-Encoding": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        }
        self.conn = pymysql.connect(host=mysqlhost, user='root', password='123456', port=3306, db='saaaa')
        self.cursor = self.conn.cursor()

    """省级"""

    def get_province_data(self, url):
        response = requests.get(url=url, headers=self.headers)
        response.encoding = 'gb2312'
        html = etree.HTML(response.text)
        provinces = html.xpath('//tr[@class="provincetr"]/td/a')
        province_list = []
        for province in provinces:
            province_url = province.xpath('./@href')[0]
            province_name = province.xpath('./text()')[0]
            province_code = province_url[:2] + '0000000000'
            province_url = parse.urljoin(response.url, province_url)
            province_info = {
                "province_url": province_url,
                "province_name": province_name,
                "province_code": province_code
            }
            province_list.append(province_info)

        # test 北京市
        # province_list = province_list[2:3]

        for p in province_list:
            data_dict = {
                'ID': p['province_code'],
                'level':Level['province'].value,
                'province': p['province_name'],
            }
            self.save_to_mysql(TABLE, data_dict)
            self.get_city_data(p['province_url'], data_dict)

    """市级"""

    def get_city_data(self, url, data_dict):
        city_list = []
        response = requests.get(url=url, headers=self.headers)
        response.encoding = 'gb2312'
        html = etree.HTML(response.text)
        citys = html.xpath('//tr[@class="citytr"]')
        for city in citys:
            city_url = city.xpath('./td[2]/a/@href')[0]
            city_name = city.xpath('./td[2]/a/text()')[0]
            city_code = city.xpath('./td[1]/a/text()')[0]
            city_url = parse.urljoin(response.url, city_url)
            city_info = {
                "city_name": city_name,
                "city_url": city_url,
                "city_code": city_code
            }
            city_list.append(city_info)

        for c in city_list:
            data_dict['ID'] = c['city_code'],
            data_dict['level'] = Level['city'].value,
            data_dict['city'] = c['city_name']
            self.save_to_mysql(TABLE, data_dict)
            self.get_county_data(c['city_url'], data_dict)
        try:
            data_dict.pop('city')
        except:
            pass

    """县级"""

    def get_county_data(self, url, data_dict):
        county_list = []
        response = requests.get(url=url, headers=self.headers)
        response.encoding = 'gb2312'
        html = etree.HTML(response.text)
        countys = html.xpath('//tr[@class="countytr"]')
        for county in countys:
            try:
                county_name = county.xpath('./td[2]/a/text()')[0]
                county_url = county.xpath('./td[2]/a/@href')[0]
                county_code = county.xpath('./td[1]/a/text()')[0]
            except:
                county_name = county.xpath('./td[2]/text()')[0]
                county_url = None
                county_code = county.xpath('./td[1]/text()')[0]
            if county_url:
                county_url = parse.urljoin(response.url, county_url)

            county_info = {
                "county_name": county_name,
                "county_url": county_url,
                "county_code": county_code
            }
            county_list.append(county_info)

        # county_list = county_list[11:]
        for cny in county_list:
            if cny["county_url"]:
                data_dict['ID'] = cny['county_code']
                data_dict['level'] = Level['county'].value,
                data_dict['county'] = cny['county_name']
                self.save_to_mysql(TABLE, data_dict)
                self.get_town_data(cny['county_url'], data_dict)
            else:
                data_dict['ID'] = cny['county_code']
                data_dict['county'] = cny['county_name']
                self.save_to_mysql(TABLE, data_dict)
        try:
            data_dict.pop('county')
        except:
            pass

    """镇级"""

    def get_town_data(self, url, data_dict):
        town_list = []
        response = requests.get(url=url, headers=self.headers)
        response.encoding = 'gb2312'
        html = etree.HTML(response.text)
        towns = html.xpath('//tr[@class="towntr"]')
        for town in towns:
            town_name = town.xpath('./td[2]/a/text()')[0]
            town_url = town.xpath('./td[2]/a/@href')[0]
            town_code = town.xpath('./td[1]/a/text()')[0]
            town_url = parse.urljoin(response.url, town_url)
            town_info = {
                "town_name": town_name,
                "town_url": town_url,
                "town_code": town_code
            }
            town_list.append(town_info)

        for town in town_list:
            data_dict['ID'] = town['town_code']
            data_dict['town'] = town['town_name']
            data_dict['level'] = Level['town'].value,
            self.save_to_mysql(TABLE, data_dict)
            self.get_village_data(town['town_url'], data_dict)
        try:
            data_dict.pop('town')
        except:
            pass

    """村级"""

    def get_village_data(self, url, data_dict):
        village_list = []
        response = requests.get(url=url, headers=self.headers)
        response.encoding = 'gb2312'
        html = etree.HTML(response.text)
        villages = html.xpath('//tr[@class="villagetr"]')
        for village in villages:
            village_code = village.xpath('./td[1]/text()')[0]
            village_code_class = village.xpath('./td[2]/text()')[0]
            village_name = village.xpath('./td[3]/text()')[0]
            village_info = {
                "village_name": village_name,
                "village_code": village_code,
                "village_class": village_code_class
            }
            village_list.append(village_info)

        list_dict_a = []
        for village in village_list:

            data_dict['ID'] = village['village_code']
            data_dict['level'] = Level['village'].value,
            data_dict['village'] = village['village_name']
            data_dict['village_class'] = village['village_class']

            dict_copy = data_dict.copy()
            list_dict_a.append(dict_copy)

        """ 遍历完之后将通过批量插入"""
        self.save_many_to_mysql(TABLE, list_dict_a)
        try:
            data_dict.pop('village')
            data_dict.pop('village_class')
        except:
            pass


    def save_to_mysql(self, table, data):
        print(data)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        try:
            if self.cursor.execute(sql, tuple(data.values())):
                print('Successful')
                self.conn.commit()
        except:
            print('Failed')
            self.conn.rollback()

    def save_many_to_mysql(self, table, data):
        print(data)
        list_data = []

        keys = ', '.join(data[0].keys())
        values = ', '.join(['%s'] * len(data[0]))
        print(keys)
        print(values)

        for d in data:
            list_data.append(tuple(d.values()))
        print(list_data)

        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        try:
            if self.cursor.executemany(sql, list_data):
                print('Successful')
                self.conn.commit()
        except:
            print('Failed')
            self.conn.rollback()

    def run(self):
        print('begin')
        self.get_province_data(BASE_URL)


if __name__ == "__main__":
    status = StatusSpider()
    status.run()
