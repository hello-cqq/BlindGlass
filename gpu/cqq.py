# -*- coding:utf-8 -*-
import json
import random
path = r"dzdp.json"
def resolveJson(path):
    file = open(path, "r")
    fileJson = json.load(file)

    return fileJson

def getPrice():
    mean_price = []
    for i in range(100):
        mean_price.append(round(random.uniform(50, 150), 1))
    return mean_price
def getCommentNum():
    num = []
    for i in range(100):
        num.append(random.randint(10,500))
    return num
def output():
    result = resolveJson(path)
    mean_price = getPrice()
    com_num = getCommentNum()
    out_v = []
    for x in result:
        _json = {}
        _json['商家名称'] = x['商家名称']
        _json['人均消费'] = mean_price[random.randint(0, 99)]
        _json['评分'] = x['评分']
        _json['评论数'] = com_num[random.randint(0, 99)]
        out_v.append(_json)
    # with open('data.json', 'a') as outfile:
    #     json.dump(out_v, outfile)
    with open('json.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(out_v, ensure_ascii=False))

output()

    
