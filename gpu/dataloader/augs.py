# -*- coding: utf-8 -*-
import torch
from torchvision import transforms
import cv2
import numpy as np
import types
from numpy import random
from shapely.geometry import box, Polygon
import math
from .image_process import *
from scipy.misc import imread, imresize


class Compose(object):
    	
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img, boxes=None, tags=None):
        for t in self.transforms:
            img, boxes, tags = t(img, boxes, tags)
        return img, boxes, tags


class Resize(object):
    def __init__(self, size=(640, 640)):
        self.width = size[1]
        self.heigth = size[0]

    def __call__(self, image, boxes=None, tags=None):
        ori_h, ori_w, _ = image.shape

        new_image = imresize(image.copy(), (self.width, self.heigth))
        if boxes is not None:
            boxes[:, :, 0] *= self.width*1.0/ori_w
            boxes[:, :, 1] *= self.heigth*1.0/ori_h
            boxes[:, :, 0] = np.clip(boxes[:, :, 0], 0, self.width)
            boxes[:, :, 1] = np.clip(boxes[:, :, 1], 0, self.heigth)
        return new_image, boxes, tags


class RandomResize(object):
    def __init__(self, longer_sides=np.arange(640, 2592, 32)):
        self.longer_sides = longer_sides

    def __call__(self, image, boxes=None, tags=None):
        return random_resize(image, boxes, tags, self.longer_sides)


class RandomRotate(object):
    def __init__(self, rotate_angles=np.arange(-10, 10, 1)):
        self.rotate_angles = rotate_angles

    def __call__(self, image, boxes=None, tags=None):
        return random_rotate(image, boxes, tags, self.rotate_angles)


class RandomRatioScale(object):
    def __init__(self, random_ratios=np.arange(0.8, 1.3, 0.1)):
        self.random_ratios = random_ratios

    def __call__(self, image, boxes, tags):
        return random_ratio_scale(image, boxes, tags, self.random_ratios)


class RandomCrop(object):
    def __init__(self, crop_size=(640, 640), max_tries=50):
        self.crop_size = crop_size
        self.max_tries = max_tries

    def __call__(self, image, boxes, tags):
        return random_crop(image, boxes, tags, self.crop_size, self.max_tries)


class RandomRotate90(object):
    def __init__(self, ratio=0.5):
        self.ratio = ratio

    def __call__(self, image, boxes, tags):
        if random.random() > self.ratio:
            return image, boxes, tags
        h, w, _ = image.shape
        image = np.rot90(image)
        new_boxes = np.zeros_like(boxes)
        for i, box in enumerate(boxes):
            new_boxes[i] = abs(box - [w, 0])
        new_boxes = new_boxes[:, (1, 2, 3, 0), :][:, :, (1, 0)]
        return image, new_boxes, tags


class PSSAugmentation(object):
    def __init__(self):
    		self.augment = Compose([RandomResize(), RandomRotate(), RandomRatioScale(), Resize()])

    def __call__(self, img, boxes, tags):
        return self.augment(img, boxes, tags)


class SythAugmentation(object):
    def __init__(self):
        self.augment = Compose([
            Resize((640, 640))
        ])

    def __call__(self, img, boxes, tags):
        return self.augment(img, boxes, tags)
