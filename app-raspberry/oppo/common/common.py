# -*- coding: UTF-8 -*-
import random
from oppo.common.global_v import *


def text2model(text):

    print(text)
    if len(text) < 7 and ('再见' in text or '拜拜' in text):
        print('exit')
        return -1
    elif len(text) < 7 and '走路模式' in text:
        print('走路模式')
        return 1
    elif len(text) < 7 and '听书模式' in text:
        print('听书模式')
        return 2
    elif len(text) < 7 and '生活模式' in text:
        print('生活模式')
        return 3
    elif len(text) < 7 and '聊天模式' in text:
        print('聊天模式')
        return 4
    else:
        print('other')
        return 0


def hello():
    index = random.randint(0, len(start_greet)-1)
    return start_greet[index]


def bye():
    index = random.randint(0, len(bye_greet)-1)
    return bye_greet[index]


def other():
    index = random.randint(0, len(other_greet)-1)
    return other_greet[index]


if __name__ == '__main__':
    print(bye())
