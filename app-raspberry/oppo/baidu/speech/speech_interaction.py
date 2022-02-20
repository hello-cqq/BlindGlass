# -*- coding: UTF-8 -*-
from aip import AipSpeech

# 百度云应用参数
APP_ID = '15592064'
API_KEY = 'sPbkhdAITExva3nasOQHru55'
SECRET_KEY = '4ysQW2aXjAPACHdn7BKcis1BgXX9V9hE'
# 初始化
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def text2sound(words):
    '''
        语音合成函数，传入欲合成的内容，返回成功与否，若成功默认将文件保存为'oppo.pcm'
    Args:
        words(str):传入的字符串
    Returns:
        boolean类型

    '''
    result = client.synthesis(words, 'zh', 1, {
        'vol': 5, 'aue': 6, 'per': 4
    })
    # 参数设置请参考官方文档

    if not isinstance(result, dict):
        with open('oppo.pcm', 'wb') as f:
            f.write(result)
        return True
    else:
        return False


def sound2text(file_path='oppo.pcm'):
    '''
        语音识别函数，传入文件名（默认为'oppo.pcm'），返回识别结果或错误代码
    Args:
        file_path(str):音频文件的路径
    Returns:
        str:语音识别的句子
    '''
    with open(file_path, 'rb') as fp:
        recog = client.asr(fp.read(), 'pcm', 16000, {
                           'dev_pid': 1536})  # 参数设置见文档
        if recog['err_no'] == 0:
            return recog['result'][0]
        return recog['err_no']


# 测试
if __name__ == '__main__':
    text2sound(
        '识别结果：黑龙江饺子馆，东砂锅东北大米，凉拌菜，酱猪爪，，，正在获取大众点评，黑龙江饺子馆,准四星商户,人均消费69.9元,评论数257条，值得推荐')
    print(sound2text('oppo.pcm'))
