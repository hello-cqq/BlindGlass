# -*- coding: UTF-8 -*-
from oppo.baidu.speech.speech_interaction import text2sound, sound2text
from oppo.raspi.audio.sound import record_sound, play_sound
from oppo.raspi.photo.camera import takePhoto
import oppo.common.global_v as gl
import re
import time
from picamera import PiCamera
import threading
import json
camera = PiCamera()
lock = threading.Lock()

class getLineThread (threading.Thread):

    def __init__(self, ws):
            threading.Thread.__init__(self)
            self.ws = ws

    def run(self):
        while self.ws and gl.flag:
            msg = {}
            msg['fromWho'] = 'raspberry'
            msg['toWho'] = 'master'
            msg['cmd'] = '2'
            msg['endpoint'] = gl.endLocation
            self.ws.send(json.dumps(msg))
            time.sleep(20)
            
class navigationThread (threading.Thread):
    '''
        多线程执行导航
    '''

    def __init__(self, ws):
            threading.Thread.__init__(self)
            self.ws = ws

    def run(self):
        if self.ws and gl.flag:
            global camera
            camera.start_preview()
            time.sleep(4)
            while self.ws and gl.flag:
                msg = takePhoto(camera, 0)
                self.ws.send(msg)
                time.sleep(25)
            camera.stop_preview()

def walkModel(ws):
    gl.flag = True
    text2sound(gl.model_greet[0])
    play_sound()
    while ws and gl.flag:
        record_sound()
        text = str(sound2text())
        v = textJudge(text)
        if v == -1:
            gl.flag = False
        elif v == 0:
            text2sound(gl.err_greet[0])
            # play_sound()
        else:
            walkModelMethods(text,ws)
    print('back walkModel')
    text2sound('走路模式已退出')
    play_sound()
    
def listenBookModel(ws):
    gl.flag = True
    text2sound(gl.model_greet[1])
    play_sound()
    while ws and gl.flag:
        record_sound()
        text = str(sound2text())
        v = textJudge(text)
        if v == -1:
            gl.flag = False
        elif v == 0:
            text2sound(gl.err_greet[1])
            play_sound()
        elif v == 1:
            global camera
            camera.start_preview()
            time.sleep(4)
            msg = takePhoto(camera, 1)
            ws.send(msg)
            time.sleep(4)
            camera.stop_preview()
        else:
            text2sound('没听清呢，再说一遍好吗')
            play_sound()
    print('back listenBookModel')
    text2sound('听书模式已退出')
    play_sound()
    
def liveModel(ws):
    gl.flag = True
    text2sound(gl.model_greet[2])
    play_sound()
    while ws and gl.flag:
        record_sound()
        text = str(sound2text())
        v = textJudge(text)
        if v == -1:
            gl.flag = False
        elif v == 0:
            text2sound(gl.err_greet[1])
            play_sound()
        elif v == 1:
            global camera
            camera.start_preview()
            time.sleep(4)
            msg = takePhoto(camera, 2)
            ws.send(msg)
            time.sleep(4)
            camera.stop_preview()
        else:
            text2sound('没听清呢，再说一遍好吗')
            play_sound()
    print('back liveModel')
    text2sound('生活模式已退出')
    play_sound()
    
def chatModel(ws):
    gl.flag = True
    text2sound(gl.model_greet[3])
    play_sound()
    while ws and gl.flag:
        record_sound()
        text = str(sound2text())
        v = textJudge(text)
        if v==-1:
            gl.flag = False
        elif v==0:
            text2sound(gl.err_greet[3])
            play_sound()
        else:
            msg = {}
            msg['fromWho'] = 'raspberry'
            msg['toWho'] = 'app'
            msg['msg'] = text
            ws.send(json.dumps(msg))
    print('back chatModel')
    text2sound('聊天模式已退出')
    play_sound()

def textJudge(text):
    print(text)
    if len(text) < 7 and ('退出' in text or '返回' in text):
        return -1
    elif '33' in text:
        return 0
    elif '拍照' in text or '阅读' in text or '识图' in text:
        return 1
    else:
        return 2
def walkModelMethods(text,ws):
    if '索' in text or '查' in text or '附近' in text:
        cate = re.compile('搜|索|查|找|询|附|最|的|近').sub('', text)
        print(cate)
        msg = {}
        msg['fromWho'] = 'raspberry'
        msg['toWho'] = 'master'
        msg['cmd'] = '1'
        msg['category'] = cate
        ws.send(json.dumps(msg))
    elif '位' in text or '哪' in text:
        text2sound('你现在位于'+gl.location)
        play_sound()
    elif '导航' in text or '前往' in text:
        t3 = navigationThread(ws)
        t3.start()
        t4 = getLineThread(ws)
        t4.start()
            
    else:
        text2sound('没听清呢，再说一遍好吗')
        # play_sound()


