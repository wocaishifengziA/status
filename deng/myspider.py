from urllib import parse
import requests
import pymysql
from lxml import etree

from status.settings import BASE_URL


class StatusSpider(object):

    def __init__(self):
        self.headers = {
            "Accept-Encoding": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        }
        self.conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', port=3306, db='saaaa')
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
            province_url = parse.urljoin(response.url, province_url)
            province_info = {
                "province_url": province_url,
                "province_name": province_name,
            }
            province_list.append(province_info)
        return province_list

    """市级"""

    def get_city_data(self, url):
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
        return city_list

    """县级"""

    def get_county_data(self, url):
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
        return county_list

    """镇级"""

    def get_town_data(self, url):
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
        return town_list

    """村级"""

    def get_village_data(self, url):
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
                "village_code_class": village_code_class
            }
            village_list.append(village_info)
        return village_list

    def save_to_mysql(self, table, data):
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

    def run(self):
        print('begin')
        province_list = self.get_province_data(BASE_URL)
        province_list = province_list[2:]
        print(province_list)

        for p in province_list:
            city_list = self.get_city_data(p["province_url"])
            for c in city_list:
                county_list = self.get_county_data(c['city_url'])
                for cny in county_list:
                    if cny["county_url"]:
                        town_list = self.get_town_data(cny["county_url"])
                        for town in town_list:
                            village_list = self.get_village_data(town["town_url"])
                            for village in village_list:
                                print(p['province_name'], c['city_name'], c['city_code'], cny['county_name'],
                                      cny['county_code'], town['town_name'], town['town_code'], village['village_name'],
                                      village['village_code'], village['village_code_class'], )
                                data_dict = {
                                    'ID': village['village_code'],
                                    'province': p['province_name'],
                                    'city': c['city_name'],
                                    'county': cny['county_name'],
                                    'town': town['town_name'],
                                    'village': village['village_name']
                                }
                                self.save_to_mysql('jkl', data_dict)
                    else:
                        data_dict = {
                            'province': p['province_name'],
                            'city': c['city_name'],
                            'county': cny['county_name'],
                        }
                        self.save_to_mysql('jkl', data_dict)


if __name__ == "__main__":
    status = StatusSpider()
    status.run()
