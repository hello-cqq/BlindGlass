# -*- coding: UTF-8 -*-
import websocket
import json
import oss2
import time
import urllib.request
from test_ocr import test_rects
# from test_scene import scene
# from ocr import get_result
# from nms_demo import shibie

'''
cqq
阿里云oss相关参数配置
'''
AccessKeyId='****'
AccessKeySecret='****'
auth = oss2.Auth(AccessKeyId,AccessKeySecret)
bucketName='****'
endpoint='http://oss-cn-shenzhen.aliyuncs.com'
bucket = oss2.Bucket(auth,endpoint,bucketName)

img_path='./photo/original/'

#define Image.class
class Image:
    '''
    图片类
    '''
    def __init__(self,fromWho,toWho,name,text,target,msg,time,date,location,cmd):
        self.fromWho = fromWho
        self.toWho = toWho
        self.name = name
        self.text = text
        self.target = target
        self.msg = msg
        self.time = time
        self.date = date
        self.location = location
        self.cmd = cmd
        
def on_message(ws, message):
    '''
    websocket接收消息,提取imgUrl调用save_photo
    '''
#   messgae:fromWho,toWho,imgName,imgUrl,currentDate,currentTime,location,cmd
    v = json.loads(message)
    print(v)
    img_path = save_photo(v['imgName'],v['imgUrl'])
    if(v['cmd']==0):
        result = scene(v['imgName'], img_path, v['location'])
        result['cmd'] = 0
    elif(v['cmd']==1):
        result = get_result(v['imgName'], img_path, v['location'])
        result['cmd'] = 1
    elif(v['cmd'] == 2):
        result = test_rects(v['imgName'], img_path, v['location'])
        result['cmd'] = 2
    upload_oss(result['name'], result['res_path'])
    i = Image('gpu','raspberry',result['name'],result['text'],result['target'],result['msg'],v['currentTime'],v['currentDate'],v['location'],result['cmd']).__dict__
    ws.send(json.dumps(i)) 
    
def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("open")
    # shibie('0081', '0081.jpg', '')
    test_rects('1', '','')

def save_photo(imgName,imgUrl):
    '''
    通过oss url下载原图并保存在本地，返回图片完整路径
    '''
    file_name = img_path+imgName+'.jpg'
    print(file_name)
    urllib.request.urlretrieve(imgUrl,filename=file_name)
    print('save success')
    return file_name

def upload_oss(img_name,img_path):
    '''
        识别后的图片上传到oss
    '''
    img_key = 'oppo/processed/'+img_name+'.jpg'
    bucket.put_object_from_file(img_key, img_path)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://www.bearboy.tech/oppo/websocket/gpu",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
