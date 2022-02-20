# -*- coding: utf-8 -*-
import os
import argparse
import io
import numpy as np
from .augs import PSSAugmentation
#from utils import generate_gt, restore_box
from .icdar2015 import ICDAR2015
from .ReCTS import RECTS
from scipy.misc import imread, imresize
import cv2
#from shapely.geometry import Polygon
from PIL import Image, ImageDraw
import torch
import torch.utils.data as data
from torchvision import transforms
#import matplotlib.pyplot as plt
from .image_process import *
parser = argparse.ArgumentParser(description = 'icdar2015 generate ground thruth')
parser.add_argument('--name', default='ic15', type=str)
parser.add_argument('--image_path', default='/workspace/zyf/dataset/icdar2015',type=str)
parser.add_argument('--is_training',default=True,type=bool)
parser.add_argument('--gt_prefix', default='gt_', type=str)
parser.add_argument('--min_text_size', default=5, type=int)
parser.add_argument('--vis_gt',default=True,type=bool)
args = parser.parse_args()
def norm(tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    for t, m, s in zip(tensor, mean, std):
        t.mul_(s).add_(m)
    return tensor

def vis_geo_map(img, geo_maps, ori_h, ori_w):
	tm, rm, bm, lm, = geo_maps
	tm_ = Image.fromarray((tm.data.cpu().numpy()/600*255).astype(np.uint8)).convert('RGB').resize((ori_w, ori_h))
	rm_ = Image.fromarray((rm.data.cpu().numpy()/600*255).astype(np.uint8)).convert('RGB').resize((ori_w, ori_h))
	bm_ = Image.fromarray((bm.data.cpu().numpy()/600*255).astype(np.uint8)).convert('RGB').resize((ori_w, ori_h))
	lm_ = Image.fromarray((lm.data.cpu().numpy()/600*255).astype(np.uint8)).convert('RGB').resize((ori_w, ori_h))
	tm_img = Image.blend(tm_, img, 0.2)
	rm_img = Image.blend(rm_, img, 0.2)
	bm_img = Image.blend(bm_, img, 0.2)
	lm_img = Image.blend(lm_, img, 0.2)
	return tm_img, rm_img, bm_img, lm_img

def vis_pss_map(img, pred_pss, ori_h, ori_w):
	im = (norm(img.data.cpu()).numpy()*255).astype(np.uint8).transpose((1, 2, 0))
	img = Image.fromarray(im).convert('RGB').resize((ori_w, ori_h))
	pss = pred_pss.data.cpu().numpy()
	pss_img = Image.fromarray((pss[0, :, :]*255).astype(np.uint8)).convert('RGB').resize((ori_w, ori_h))
	pss_img = Image.blend(pss_img, img, 0.5)
	return img, pss_img

def vis_boxes(img, boxes):
	#img = Image.fromarray(img)
	img_draw = ImageDraw.Draw(img)
	if len(boxes) == 0:
		return img
	for ind, poly in enumerate(boxes):
		img_draw.line([poly[0, 0], poly[0, 1], poly[1, 0], poly[1, 1], poly[2, 0], poly[2, 1], poly[3, 0], poly[3, 1], poly[0, 0], poly[0, 1]], width=4, fill=(0, 255, 0))
		x_min = np.min(poly[:,0])
		y_min = np.min(poly[:,1])
		x_max = np.max(poly[:,0])
		y_max = np.max(poly[:,1])
		#img_draw.line([x_min, y_min, x_max, y_min, x_max, y_max, x_min, y_max, x_min, y_min], width=4, fill=(255, 0, 0))
	return img

def vis_multi_image(image_list, shape=[1,-1]):
	image_num = len(image_list)
	h, w,_ = np.array(image_list[0]).shape
	num_w = image_num/shape[0]
	num_h = shape[0]
	new_im = Image.new('RGB', (int(num_w*w),int(num_h*h)))
	for idx, image in enumerate(image_list):
		idx_w = idx%num_w
		idx_h = idx/num_w
		new_im.paste(image, (int(idx_w*w),int(idx_h*h)))
	return new_im

def vis_gt(im, text_polys, text_tags, pss_maps,geo_maps, agl_maps, training_mask, image_name):
    img = im.copy()[:, :, (0, 1, 2)].astype(np.uint8)
    h, w, c = img.shape
    img = Image.fromarray(img)
    img_draw = ImageDraw.Draw(img)
    for ind, poly in enumerate(text_polys):
        if text_tags[ind] == False:
            img_draw.line([poly[0, 0], poly[0, 1], poly[1, 0], poly[1, 1], poly[2, 0], poly[2, 1], poly[3, 0], poly[3, 1], poly[0, 0], poly[0, 1]], width=4, fill=(0, 255, 0))
    pss_maps = Image.fromarray(pss_maps*255).convert('RGB')
    pss_img = Image.blend(img, pss_maps, 0.5)
    geo_map_1 = Image.fromarray(geo_maps[0]*255).convert('RGB')
    geo1_img = Image.blend(img, geo_map_1, 0.5)
    geo_map_2 = Image.fromarray(geo_maps[1]*255).convert('RGB')
    geo2_img = Image.blend(img, geo_map_2, 0.5)
    geo_map_3 = Image.fromarray(geo_maps[2]*255).convert('RGB')
    geo3_img = Image.blend(img, geo_map_3, 0.5)
    geo_map_4 = Image.fromarray(geo_maps[3]*255).convert('RGB')
    geo4_img = Image.blend(img, geo_map_4, 0.5)

    agl_map = Image.fromarray((agl_maps/np.pi + 0.5)*255).convert('RGB')
    agl_img = Image.blend(img, agl_map, 0.5)

    mask_img = Image.blend(img, Image.fromarray(training_mask*255).convert('RGB'), 0.5)

    new_im = Image.new('RGB', (w*4, h*2))


    x_offset = 0
    for idx, tm in enumerate([img, pss_img, agl_img,mask_img, geo1_img,geo2_img,geo3_img,geo4_img]):
        idx_h = idx/4
        idx_w = idx%4
        if tm!=None:
        	new_im.paste(tm, (w * idx_w,h * idx_h))
    if os.path.exists('./outputs') == False:
        os.mkdir('./outputs')
    if os.path.exists('./outputs/eval_gt_') == False:
        os.mkdir('./outputs/eval_gt_')
    new_im.save('./outputs/eval_gt_/' + image_name)
def vis_pred(im, text_polys, pss_maps,geo_maps, agl_maps, image_name):
	def save_image(img, image_name):
		if os.path.exists('./outputs') == False:
		    os.mkdir('./outputs')
		if os.path.exists('./outputs/eval_gt_') == False:
		    os.mkdir('./outputs/eval_gt_')
		img.save('./outputs/eval_gt_/' + image_name)
	img = im.copy()[:, :, (0, 1, 2)].astype(np.uint8)
	h, w, c = img.shape
	img = Image.fromarray(img)
	img_draw = ImageDraw.Draw(img)
	if len(text_polys) == 0:
		save_image(img, image_name)
	for ind, poly in enumerate(text_polys):
		img_draw.line([poly[0, 0], poly[0, 1], poly[1, 0], poly[1, 1], poly[2, 0], poly[2, 1], poly[3, 0], poly[3, 1], poly[0, 0], poly[0, 1]], width=4, fill=(0, 255, 0))
	save_image(img, image_name)

def load_ann(gt_paths):
    res = []
    for gt in gt_paths:
        item = {}
        item['polys'] = []
        item['tags'] = []
        reader = open(gt).readlines()
        for line in reader:
            parts = line.strip().split(',')
            label = parts[-1]
            line = [i.strip('\ufeff').strip('\xef\xbb\xbf') for i in parts]
            x1, y1, x2, y2, x3, y3, x4, y4 = list(map(float, line[:8]))
            item['polys'].append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
            if label == '###':
                item['tags'].append(True)
            else:
                item['tags'].append(False)
        item['polys'] = np.array(item['polys'], dtype=np.float32)
        item['tags'] = np.array(item['tags'], dtype=np.bool)
        item['path'] = gt
        res.append(item)
    return res


# class ICDAR2015(object):
# 	def __init__(self,args):
# 		self.args = args
# 		self.generate_information()
# 	def generate_information(self):
# 		self.is_training = self.args.is_training
# 		if self.is_training:
# 			image_floder = os.path.join(self.args.image_path, 'train_images')
# 			gt_floder = os.path.join(self.args.image_path, 'train_gts')
# 			self.image_path_list = [os.path.join(image_floder, image) for image in os.listdir(image_floder)]
# 			gt_path_list    = [os.path.join(gt_floder, gt) for gt in os.listdir(gt_floder)]
# 			self.image_path_list = sorted(self.image_path_list)
# 			gt_path_list = sorted(gt_path_list)
# 			self.targets = load_ann(gt_path_list)
# 		else:
# 			image_floder = os.path.join(self.args.image_path, 'test_images')
# 			self.image_path_list = [os.path.join(image_floder, image) for image in os.listdir(image_floder)]
# 			self.image_path_list = sorted(self.image_path_list)
# 	def len(self):
# 		return len(self.image_path_list)
class Dataset(data.Dataset):
    def __init__(self, dataset,path):
    	self.dataset = eval(dataset)(path)
    	self.augment = PSSAugmentation()
    	normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    	self.transformer  = transforms.Compose([
            transforms.ToTensor(),
            normalize,
        ])
    def __len__(self):
    	return self.dataset.len()
    def __getitem__(self, index):
    	#img = imread(image_path) #h,w,c
        if self.dataset.is_training:
            path, polys, texts = self.dataset.getitem(index)
            img = imread(path, mode='RGB')
            aug_img, boxes, tags = self.augment(img, polys, texts)
        	# aug_img, boxes, tags = img, polys, tags
        	# aug_img = imresize(img.copy(), (self.dataset.args.test_height, self.dataset.args.test_width))
            h, w, _ = aug_img.shape
        	# pss_maps,geo_maps, agl_maps, training_mask = generate_rbox((h, w), boxes, tags)
            pss_maps,geo_maps, agl_maps, training_mask= generate_gt((h, w), boxes, tags)
            transform_img = self.transformer(aug_img.astype(np.uint8))
            pss_maps = torch.Tensor(pss_maps)
            geo_maps = torch.Tensor(geo_maps)
            agl_maps = torch.Tensor(agl_maps)
            training_mask = torch.Tensor(training_mask)
            out = torch.cat([transform_img,pss_maps,geo_maps,agl_maps,training_mask],dim=0)
            return out, path
def text_collate(batch):
    outs,paths = [], []
    for sample in batch:
        outs.append(sample[0])
        paths.append(sample[1])
    outs = torch.stack(outs, 0)
    return outs, paths

from numpy import random
def main():
	cfg = {'dataset': 'ICDAR2015', 'path': '/workspace/zyf/dataset/icdar2015'}
	ic15 = Dataset(cfg['dataset'], cfg['path'])
	out, path = ic15[0]
	print(path)

def test_loader():
	from torch.utils import data
	icdar2015 = ICDAR2015(args)
	dataset = Dataset(icdar2015)
	dataloader = data.DataLoader(dataset, 1, num_workers=0, collate_fn= text_collate, shuffle=False, pin_memory=True)
	for i in range(50):
		for j, sample in enumerate(dataloader, 0):
			imgs, true_pss, true_geo, true_agl, training_masks, paths = sample
			#restore_box(true_pss[0].data.cpu().numpy(), true_geo[0].data.cpu().numpy(), true_agl[0].data.cpu().numpy())
			print (i,paths[0])
def test_restore_box():
	icdar2015 = ICDAR2015(args)
	for idx in range(icdar2015.len()):
		print(icdar2015.targets[idx]['path'])
		image_path = icdar2015.image_path_list[idx]
		boxes = icdar2015.targets[idx]['polys']
		tags = icdar2015.targets[idx]['tags']
		img = imread(image_path)
		h, w, _ = img.shape
		pss_maps,geo_maps, agl_maps, training_mask = generate_gt((h, w), boxes, tags, args)
		pss_maps = pss_maps[:,::4,::4]
		geo_maps = geo_maps[:,::4,::4]
		agl_maps = agl_maps[:,::4,::4]
		training_mask = training_mask[:,::4,::4]
		print (pss_maps.shape)
		restored_boxes = restore_box(pss_maps[0],geo_maps, agl_maps[0], 4)
		vis_pred(img, restored_boxes,pss_maps[0],geo_maps, agl_maps[0], image_path.split('/')[-1])


if __name__ == '__main__':
	main()
	#test_loader()
	#test_restore_box()
    #cfg={'dataset':'ICDAR2015','path':'/workspace/zyf/dataset/icdar2015'}
    #ic15 = Dataset(cfg['dataset'],cfg['path'])
    #dataloader = data.DataLoader(ic15, 1, num_workers=0, collate_fn= text_collate, shuffle=False, pin_memory=True)
    #for j, sample in enumerate(dataloader, 0):
        #out, path = sample
        #print(path)
        #print(out.shape)


