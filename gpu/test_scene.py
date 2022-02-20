# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import cv2
import model
import os
import time
from nms_demo import shibie
from test import mangdao

def scene(img_name, img_path, location):
    # image_dir = '0081.jpg'
    logdir = 'logs_scene'
    position = {0: 'street!',
                1: 'crossroads!',
                2: 'building!',
                }
    scene_model = model.Model(num_classes=3, image_size=640)
    scene_model.build()
    saver = tf.train.Saver(tf.global_variables(),
                        max_to_keep=None)

    gpu_options = tf.GPUOptions(allow_growth=True)
    sess_config = tf.ConfigProto(gpu_options=gpu_options)

    sess = tf.Session(config=sess_config)
    model_path = tf.train.latest_checkpoint(logdir)
    saver.restore(sess, model_path)
    image_dir = img_path

    start = time.time()
    image = cv2.imread(image_dir)
    image = cv2.resize(image, (640, 640), interpolation=cv2.INTER_CUBIC)
    image = np.expand_dims(image, axis=0)
    predict = sess.run([scene_model.predict], feed_dict={"data_feed:0": image,
                                                       "is_training:0": False})
    end = time.time()
    print("scene time: " + str(end - start))
    index = predict[0][0]
    print(position[index])
    tf.reset_default_graph()
    if index==1:
        return shibie(img_name, img_path, location)
    elif index==0:
        return mangdao(img_name, img_path, location)
    elif index==2:
        return buildingResult(img_name, img_path, location)
    else:
        return defaultResult(img_name, img_path, location)


def buildingResult(img_name, img_path, location):
    result = {}
    result['name'] = img_name
    result['res_path'] = './photo/original/'+img_name+'.jpg'
    result['text'] = '暂未识别'
    result['target'] = '建筑物'
    result['msg'] = '附近建筑物较多，请注意安全'

def defaultResult(img_name, img_path, location):
    result = {}
    result['name'] = img_name
    result['res_path'] = './photo/original/'+img_name+'.jpg'
    result['text'] = '暂未识别'
    result['target'] = '暂未识别'
    result['msg'] = ''
if __name__ == '__main__':
    scene('0081', '0081.jpg', '')
