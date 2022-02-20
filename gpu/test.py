# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import cv2
import model
import time

def mangdao(img_name, img_path, location):
    '''
    盲道监测入口函数
    Args：
        img_name:图片名字
        img_path:图片路径
        locaation:拍摄地点
    Returns:
        result:json字符串，包含图片完整信息
    '''
    logdir = 'logs_mangdao'
    position = {0: '盲道在你脚下，可以正常直行',
                1: '盲道在你左边,请稍微向左移动一下',
                2: '盲道在你右边,请稍微向右移动一下',
                3: '盲道在你的正前方，请前往靠近',
                4: '这附近没有盲道，请谨慎前行'
                }

    #os.environ["CUDA_VISIBLE_DEVICES"] = '1'

    # 调用model类创建模型
    md_model = model.Model(num_classes=5, image_size=640)
    md_model.build()
    saver = tf.train.Saver(tf.global_variables(),
                        max_to_keep=None)

    gpu_options = tf.GPUOptions(allow_growth=True)
    sess_config = tf.ConfigProto(gpu_options=gpu_options)

    sess = tf.Session(config=sess_config)
    model_path = tf.train.latest_checkpoint(logdir)
    saver.restore(sess, model_path)
    result = {}
    result['name'] = img_name
    result['res_path'] = './photo/original/'+img_name+'.jpg'
    # image_dir = '0081.jpg'
    image_dir = img_path

    start = time.time()
    image = cv2.imread(image_dir)
    image = cv2.resize(image, (640, 640), interpolation=cv2.INTER_CUBIC)
    image = np.expand_dims(image, axis=0)
    predict = sess.run([md_model.predict], feed_dict={"data_feed:0": image,
                                                    "is_training:0": False})
    end = time.time()
    print("total time: " + str(end - start))
    tf.reset_default_graph()
    result['text'] = '暂未识别'
    result['target'] = '街道'
    result['msg'] = '你正在街道上，'+position[predict[0][0]]
    print(position[predict[0][0]])
    return result

if __name__ == '__main__':
    mangdao('0081','0081.jpg','diqiu')
    time.sleep(5)
    mangdao('0081', '0081.jpg', 'diqiu')
