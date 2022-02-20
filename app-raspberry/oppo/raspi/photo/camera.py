# -*- coding: UTF-8 -*-
import oss2
import time
import re
import json
from time import sleep
import oppo.common.global_v as gl
AccessKeyId='LTAIvG7SkQpSFaBf'
AccessKeySecret='GLcBCI3ifC3r9FY0nlrnPSHTx66hvj'
auth = oss2.Auth(AccessKeyId,AccessKeySecret)
bucketName='bearboy'
endpoint='http://oss-cn-shenzhen.aliyuncs.com'
bucket = oss2.Bucket(auth,endpoint,bucketName)
#define Image.class
class Image:
    '''
        图片类
    '''
    def __init__(self,fromWho,toWho,imgName,imgUrl,currentDate,currentTime,location,cmd):
        self.fromWho = fromWho
        self.toWho = toWho
        self.imgName = imgName
        self.imgUrl = imgUrl
        self.currentDate = currentDate
        self.currentTime = currentTime
        self.location = location
        self.cmd = cmd

def takePhoto(camera,cmd):
    '''
        拍照函数
        Args:
            location(str):当前地点
            cmd(int):0->红绿灯检测;1->盲道检测
    '''
    img_name='photo.jpg'
    camera.capture(img_name)
    '''
        上传原图到阿里云oss
       
    '''
    img_path = 'photo.jpg'
    nowDate = time.strftime("%Y-%m-%d", time.localtime())
    nowTime = time.strftime("%H:%M:%S", time.localtime())
    name = re.sub(r'\D', "", nowDate)+re.sub(r'\D', "", nowTime)
    img_key = 'oppo/photos/'+name+'.jpg'
    bucket.put_object_from_file(img_key, img_path)
    imgUrl = 'https://bearboy.tech/'+img_key
    i = Image('raspberry', 'gpu', name, imgUrl, nowDate,
              nowTime, gl.location, cmd).__dict__
    return json.dumps(i)

#测试
if __name__ == '__main__':
    takePhoto()
    
    
