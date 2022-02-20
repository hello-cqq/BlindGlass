import os
import numpy as np
import json
from bilib import sort_nicely
import sys


def load_ann(gt_paths):
    reload(sys)
    sys.setdefaultencoding("utf-8")
    res = []
    for gt in gt_paths:
        item = {}
        item['polys'] = []
        item['tags'] = []
        item['texts'] = []
        item['paths'] = gt
        with open(gt) as json_file:
            result = json.load(json_file)
        result = result['lines']
        for i in range(len(result)):
            label = result[i]['transcription']
            x1, y1, x2, y2, x3, y3, x4, y4 = result[i]['points']
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


class RECTS(object):
    def __init__(self, path):
        self.generate_information(path)

    def generate_information(self, path):
        self.is_training = True  # config['is_training']
        if self.is_training:
            image_floder = os.path.join(path, 'img')
            gt_floder = os.path.join(path, 'gt')
            train_txt = os.path.join(path, 'train.txt')
            image_names = np.loadtxt(train_txt, dtype=np.str)
            self.image_path_list = [os.path.join(
                image_floder, image) for image in image_names]
            gt_path_list = [os.path.join(gt_floder, gt).replace(
                'jpg', 'json') for gt in image_names]
            self.image_path_list = sort_nicely(self.image_path_list)
            gt_path_list = sort_nicely(gt_path_list)
            self.targets = load_ann(gt_path_list)

    def len(self):
        return len(self.image_path_list)

    def getitem(self, index):
        return self.image_path_list[index], self.targets[index]['polys'].copy(), self.targets[index]['texts'].copy()


def main():
    config = {'is_training': True,
              'image_path': '/workspace/zyf/dataset/ReCTS'}
    rects = RECTS(config['image_path'])
    char_list = []
    for t in rects.targets:
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
