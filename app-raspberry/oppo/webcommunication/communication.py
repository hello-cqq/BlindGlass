# -*- coding: UTF-8 -*-
import websocket
import threading
import requests
import time
'''
cqq
'''
import oppo.webcommunication.model as mod
from oppo.baidu.speech.speech_interaction import text2sound, sound2text
from oppo.raspi.audio.sound import record_sound, play_sound
from oppo.common.common import text2model, hello, bye, other
import oppo.common.global_v as gl
import json


class modelThread (threading.Thread):
    '''
        多线程执行录音和播放
    '''

    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws

    def run(self):
        while self.ws:
            setModel(self.ws)


class locationThread (threading.Thread):
    '''
        多线程执行定位
    '''

    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws

    def run(self):
        while self.ws:
            getLocation(self.ws)


def on_message(ws, message):
    '''
    websocket的接收信息方法,并判断消息是来自监护人还是gpu，做不同解析
    '''
    print(message)
    v = json.loads(message)
    if v['fromWho'] == 'gpu':
        data = {'name': v['name'], 'text': v['text'], 'target': v['target'],
                'msg': v['msg'], 'time': v['time'], 'date': v['date'], 'location': v['location']}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        requests.post('http://www.bearboy.tech/oppo/SaveImgServlet',
                      data=data, headers=headers)
        gl.gpu_msg = v['msg']
        print(gl.gpu_msg)
        if v['cmd'] != 0:
            text2sound(gl.gpu_msg)
            play_sound()
        else:
            text2sound('当前坐标,'+gl.streetLocation+',' +
                       gl.walkLine[0]+','+gl.walkLine[1]+','+gl.gpu_msg)
            play_sound()

    elif v['fromWho'] == 'master':
        if v['cmd'] == '0':
            r = v['location']
            gl.location = r['district']+r['street']+r['poiName']
            gl.streetLocation = r['street']+r['poiName']
            print(gl.location)
        elif v['cmd'] == '1':
            gl.master_msg = v['msg']
            gl.endLocation = v['name']
            print(gl.master_msg)
            text2sound(gl.master_msg)
            play_sound()
        elif v['cmd'] == '2':
            gl.walkLine = v['walkLine']
            print(gl.walkLine)
    elif v['fromWho'] == 'app':
        gl.chat_msg = v['msg']
        text2sound(gl.chat_msg)
        play_sound()


def on_error(ws, error):
    print(error)
    text2sound('发生错误')
    play_sound()


def on_close(ws):
    print("closed")
    text2sound('拜拜')
    play_sound()


def on_open(ws):
    print("websocket opened")
    text2sound(hello())
    play_sound()
    t1 = modelThread(ws)
    t2 = locationThread(ws)
    t1.start()
    t2.start()


def getLocation(ws):
    msg = {}
    msg['fromWho'] = 'raspberry'
    msg['toWho'] = 'master'
    msg['cmd'] = '0'
    try:
        while ws:
            ws.send(json.dumps(msg))
            time.sleep(15)
    except:
        print('getLocation出现异常')


def setModel(ws):
    '''
        对语音识别的结果根据不同指令发送不同数据格式,进入不同模式
    '''
    record_sound()
    text = str(sound2text())
    value = text2model(text)
    if value == -1:
        '''
            关闭websocket
        '''
        text2sound(bye())
        play_sound()
        ws.close()
    elif value == 0:
        '''
            其他
        '''
        text2sound(other())
        play_sound()

    elif value == 1:
        '''
            走路模式
        '''
        mod.walkModel(ws)
    elif value == 2:
        '''
            听书模式
        '''
        mod.listenBookModel(ws)
    elif value == 3:
        '''
            生活模式
        '''
        mod.liveModel(ws)
    elif value == 4:
        '''
            聊天模式
        '''
        mod.chatModel(ws)


def connection(socket_url):
    '''
    websocket连接
    Args:
    socket_url(str):服务器地址
    '''
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(socket_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
