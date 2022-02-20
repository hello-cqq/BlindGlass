# -*- coding:utf-8 -*-
import re
from bs4 import BeautifulSoup
import json
from requests import Session
import time


class dzdp:
    def __init__(self, url):
        self.info = []
        self.baseUrl = url
        self.page = 1
        self.pagenum = 27  # 设置最大页面数目
        self.headers = {
            "Host": "www.dianping.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
            "Referer": "http://www.dianping.com/",
        }

    def start(self):
        self.s = Session()  # 定义一个Session()对象
        print(self.baseUrl)
        print("start")
        dzdp.parseHtml(self, self.baseUrl)  # 调用__parseHtml函数
        print('end')

    def parseHtml(self, preUrl):
        _json = dict()  # 定义一个字典用以存储数据
        html = self.s.post(preUrl, headers=self.headers).text  # 发送请求，获取html

        soup = BeautifulSoup(html, 'lxml')  # 进行解析
        name = ['商家名称', '评论数量', '人均消费', '评分']
        for li in soup.find('div', class_="shop-wrap").find('div', id="shop-all-list").ul.find_all('li'):
            info = li.find('div', class_='txt')
            try:
                _json[name[0]] = info.find(
                    'div', class_='tit').a.h4.get_text()
                # print(_json[name[0]])
            except:
                _json[name[0]] = 'no'
            try:
                _json[name[1]] = info.find('div', class_='comment').find(
                    'a', class_="review-num").b.get_text()
                # print(_json[name[1]])
            except:
                _json[name[1]] = 'no'
            try:
                _json[name[2]] = re.sub('￥', '', info.find('div', class_='comment').find(
                    'a', class_="mean-price").b.get_text())
                # print(_json[name[2]])
            except:
                _json[name[2]] = 'no'
            try:
                _json[name[3]] = info.find('div', class_='comment').find(
                    'span').attrs['title']
                # print(_json[name[3]])
            except:
                _json[name[3]] = 'no'

            with open('dzdp.json', 'a') as outfile:
                json.dump(_json, outfile)
            with open('dzdp.json', 'a') as outfile:
                outfile.write(',\n')
        time.sleep(4)
        self.page += 1
        if self.page <= self.pagenum:
            dzdp.parseHtml(self, self.baseUrl+'d500p'+str(self.page))


if __name__ == '__main__':
    url = r'http://www.dianping.com/wuhan/ch0/r6320'
    d = dzdp(url)
    d.start()
