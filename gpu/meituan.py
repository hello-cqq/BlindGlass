# -*- coding:utf-8 -*-
import re
from bs4 import BeautifulSoup
import json
from requests import Session
import time
class dzdp:
    def __init__(self, url):
        self.baseUrl = url
        self.page = 1
        self.pagenum = 27  # 设置最大页面数目
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0"
        }

    def start(self):
        self.s = Session()  # 定义一个Session()对象
        print (self.baseUrl)
        print ("start")
        dzdp.parseHtml(self,self.baseUrl)  # 调用__parseHtml函数
        print ('end')

    def parseHtml(self,preUrl):
        _json = dict()  # 定义一个字典用以存储数据
        html = self.s.post(preUrl).text  # 发送请求，获取html
        soup = BeautifulSoup(html, 'html.parser')  # 进行解析
        name = ['商家名称', '评论数量', '人均消费', '评分']
        for li in soup.find('div', class_="common-list-main").find_all('div'):
            info = li.find('div', class_='default-card').find('div',
                                                              class_='default-list-item clearfix').find('div', class_='list-item-desc').find('div', class_='list-item-desc-top')
            
            _json[name[0]] = info.find(
                'a', class_='link item-title').get_text()
            _json[name[1]] = info.find('div', class_='item-eval-info clearfix').find(
                'span', class_="highlight").get_text()
            _json[name[2]] = info.find('div', class_='item-bottom-info clearfix').find(
                'div', class_="item-price-info").get_text()
            _json[name[3]] = info.find('div', class_='item-eval-info clearfix').find_all(
                'span')[0].get_text()
            with open('dzdp.json', 'a') as outfile:
                json.dump(_json, outfile, ensure_ascii=False)
            with open('dzdp.json', 'a') as outfile:
                outfile.write(',\n')
        time.sleep(4)
        self.page += 1
        if self.page <= self.pagenum:
            dzdp.parseHtml(self, self.baseUrl+'d500p'+str(self.page))


if __name__ == '__main__':
    url = r'https://wh.meituan.com/s/华中科技大学/'
    d = dzdp(url)
    d.start()
