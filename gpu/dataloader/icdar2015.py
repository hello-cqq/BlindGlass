# -*- coding: utf-8 -*-
import os
import numpy as np
from bilib import sort_nicely
import io
import cv2


def load_ann(gt_paths):
    res = []
    for gt in gt_paths:
        item = {}
        item['polys'] = []
        item['tags'] = []
        item['texts'] = []
        item['paths'] = gt
        reader = open(gt).readlines()
        #reader = io.open(gt, 'r', encoding='UTF-8').readlines()
        for line in reader:
            parts = line.strip().split(',')
            label = parts[-1]
            line = [i.strip('\ufeff').strip('\xef\xbb\xbf') for i in parts]
            #x1, y1, x2, y2, x3, y3, x4, y4 = list(map(float, line[:8]))
            x1, y1, x4, y4, x3, y3, x2, y2 = list(map(float, line[:8]))
            item['polys'].append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
            item['texts'].append(label)
            if label == '###':
                item['tags'].append(True)
            else:
                item['tags'].append(False)
        item['polys'] = np.array(item['polys'], dtype=np.float32)
        item['tags'] = np.array(item['tags'], dtype=np.bool)
        item['texts'] = np.array(item['texts'], dtype=np.str)
        res.append(item)
    #     print('read',item['polys'])
    # exit()
    return res


def load_ann_wtmi(gt_paths):
    res = []
    for gt in gt_paths:
        item = {}
        item['polys'] = []
        item['tags'] = []
        item['texts'] = []
        item['paths'] = gt
        #reader = open(gt).readlines()
        reader = io.open(gt, 'r', encoding='UTF-8').readlines()
        for line in reader:
            parts = line.strip().split(',')
            label = parts[-1]
            line = [i.strip('\ufeff').strip('\xef\xbb\xbf') for i in parts]
            x1, y1, x4, y4, x3, y3, x2, y2 = list(map(float, line[:8]))
            item['polys'].append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
            item['texts'].append(label)
            if label == '###':
                item['tags'].append(True)
            else:
                item['tags'].append(False)
        item['polys'] = np.array(item['polys'], dtype=np.float32)
        item['tags'] = np.array(item['tags'], dtype=np.bool)
        item['texts'] = np.array(item['texts'], dtype=np.str)
        res.append(item)
    #     print('read',item['polys'])
    # exit()
    return res


class ICDAR2015(object):
    def __init__(self, path, is_training=True):
        self.is_training = is_training
        self.generate_information(path)

    def generate_information(self, path):
        if self.is_training:
            image_floder = os.path.join(path, 'train_images')
            gt_floder = os.path.join(path, 'train_gts')
            self.image_path_list = [os.path.join(
                image_floder, image) for image in os.listdir(image_floder)]
            gt_path_list = [os.path.join(gt_floder, gt)
                            for gt in os.listdir(gt_floder)]
            self.image_path_list = sort_nicely(self.image_path_list)
            gt_path_list = sort_nicely(gt_path_list)
            self.targets = load_ann(gt_path_list)
            #self.targets = load_ann_wtmi(gt_path_list)
        else:
            image_floder = os.path.join(path, 'test_images')
            self.image_path_list = [os.path.join(
                image_floder, image) for image in os.listdir(image_floder)]
            self.image_path_list = sort_nicely(self.image_path_list)

    def len(self):
        return len(self.image_path_list)

    def getitem(self, index):
        return self.image_path_list[index], self.targets[index]['polys'].copy(), self.targets[index]['texts'].copy()


def main():
    config = {'is_training': True,
              'image_path': '/workspace/zyf/dataset/icdar2015'}
    icdar2015 = ICDAR2015(config['image_path'])
    char_list = []
    for t in icdar2015.targets:
        print(t)
        for text in t['texts']:
            for char in text:
                if char not in char_list:
                    char_list.append(char)
    print(sorted(char_list))


    # for index in range(icdar2015.len()):
    # 	image =
if __name__ == '__main__':
    main()
