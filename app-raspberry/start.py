# -*- coding: UTF-8 -*-
from oppo.baidu.speech.speech_interaction import sound2text
from oppo.raspi.audio.sound import record_sound
from oppo.common.wake import wake
'''
raspberry的启动程序,唤醒树莓派websocket服务
'''
def start():
    '''
    websocket启动函数，通过不断循环判断语音关键字是否可以唤醒树莓派
    '''
    while True:
        record_sound()
        text = str(sound2text())
        '''
            调用唤醒判断函数
        '''
        wake(text)
        
if __name__ == '__main__':
    start()