# -*- coding: UTF-8 -*-
from oppo.webcommunication.communication import connection

socket_url = 'ws://www.bearboy.tech/oppo/websocket/raspberry'

def wake(text):
    '''
        唤醒树莓派websocket服务
    Args；
        text(str):语音识别的结果,唤醒的关键词是包含'小欧'
        结果如下：
            小欧醒了和小欧没醒
    '''
    print(text)
    if len(text)<7 and '小欧' in text:
        print('小欧醒了')
        connection(socket_url)
    else:
        print('小欧没醒')
