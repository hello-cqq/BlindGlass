# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import glob
import numpy as np
from bilib.misc_utils import sort_nicely

# 从目录中读取图片和标签
def load_data(data_dir, label_dir):
    '''
    从目录中读取图片和标签
    '''
    images = []
    # 得到目录中所有图片的绝对路径
    image_paths = sort_nicely(glob.glob(data_dir + '/*.jpg'))
    # 读取图片并改变图片大小
    for i in range(len(image_paths)):
        image = cv2.imread(image_paths[i])
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_CUBIC)
        images.append(image)
    # 将list类型的图片组转成ndarray
    images = np.array(images)
    # 读取标签
    labels = np.loadtxt(label_dir, dtype=np.int64)
    return images, labels
