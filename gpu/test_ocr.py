# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import imageio
import json
# sys.path.append(os.getcwd())


# crnn packages
from torch.autograd import Variable
from crnn_package import utils
from crnn_package import dataset
import crnn_package.models.crnn as crnn
from crnn_package import alphabets

import torch
from models.detect import Detect
from scipy.misc import imread, imresize
from dataloader.dataset import vis_pss_map, vis_multi_image, vis_boxes, vis_geo_map
from torch.utils import data
from dataloader.utils import restore_box_gpu, nms_locality, reselect_box, get_mini_boxes
import os
from test_ocr_config import test_config
import time
import numpy as np
import cv2
from torchvision import transforms
from PIL import Image
import rotate

dp_json = json.load(open('data.json', "r"))
# os.environ["CUDA_VISIBLE_DEVICES"] = test_config['CARD_ID']
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
transformer = transforms.Compose([
    transforms.ToTensor(),
    normalize
])
def norm(tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    for t, m, s in zip(tensor, mean, std):
        t.mul_(s).add_(m)
    return tensor


def save_result(image_name, new_in, keep_box, epoch_num, save_dir, test_size, nms_thred, reselect_thred, dataset='rects'):
    save_floder = os.path.join(save_dir, '')
    image_info = str(test_size[1])+'_'+str(test_size[0])+'_' + \
        epoch_num+'_n'+str(nms_thred)+'_r'+str(reselect_thred)
    vis_image_path = os.path.join(save_floder, '', '')
    vis_text_path = os.path.join(save_floder, '', '')
    if os.path.exists(vis_image_path) == False:
        os.makedirs(vis_image_path)
        os.makedirs(vis_text_path)
    keep_box = keep_box.astype(np.int32)
    res_name = vis_text_path + '/' + image_name + '.txt'
    new_in.save(vis_image_path+'/' + image_name + '.jpg')
    fp = open(res_name, 'w')
    for box in keep_box:
        temp_x = []
        temp_y = []
        temp = []
        box = box.reshape(-1)
        for j in range(len(box)):
            if j % 2 == 0:
                temp_x.append(box[j])
                temp.append(str(box[j]))
            else:
                temp_y.append(box[j])
                temp.append(str(box[j]))
        fp.write(','.join(temp) + '\n')
    fp.close()
    return vis_text_path, os.path.join(save_floder, image_info)


def get_boxes_from_pss(seg_pred, thre=0.5):
    ret, tmap = cv2.threshold(seg_pred, thre, 1, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        (tmap * 255).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    boxes, ssides = [], []
    for cnt in contours:
        points = get_mini_boxes(cnt)
        boxes.append(points)
    return np.array(boxes).reshape([-1, 4, 2])


def crnn_recognition(cropped_image, model):
    str1 = alphabets.alphabet
    alphabet = str1
    converter = utils.strLabelConverter(alphabet)

    image = cropped_image.convert('L')
    w = int(image.size[0] / (280 * 1.0 / 160))
    transformer = dataset.resizeNormalize((w, 32))
    image = transformer(image)
    if torch.cuda.is_available():
        image = image.cuda()
    image = image.view(1, *image.size())
    image = Variable(image)

    model.eval()
    preds = model(image)

    _, preds = preds.max(2)
    preds = preds.transpose(1, 0).contiguous().view(-1)

    preds_size = Variable(torch.IntTensor([preds.size(0)]))
    sim_pred = converter.decode(preds.data, preds_size.data, raw=False)
    return sim_pred


def test_rects(img_name, img_path, location):
    new_h, new_w = test_config['test_size']
    net = Detect('resnet50')
    net = torch.nn.DataParallel(net).cuda()
    net.load_state_dict(torch.load(test_config['model']))
    net.eval()
    for v in net.parameters():
        v.requires_grad = False
    start = 0
    image = imread(os.path.join(
        test_config['path'], img_name+'.jpg'), mode='RGB')
    h, w = image.shape[:2]
    image = imresize(image, (h // 2, w // 2))
    h, w = image.shape[:2]
    new_w = w * 1.0 / h * new_h
    new_w = int(new_w)
    if new_w % 32 >= 16:
        new_w = new_w + 32 - new_w % 32
    else:
        new_w = new_w - new_w % 32
    image_resied = imresize(image.copy(), (new_h, new_w))
    imgs = transformer(image_resied.astype(np.uint8))[None, :, :, :].cuda()

    scale_h = h * 1.0 / new_h
    scale_w = w * 1.0 / new_w
    pred_pss, pred_geo, pred_agl = net(imgs)
    boxes, scores = restore_box_gpu(
        pred_pss, pred_geo, pred_agl, scale_factor_w=4, scale_factor_h=4)
    polys = np.concatenate(
        [boxes[0].reshape((-1, 8)), scores[0].reshape((-1, 1))], 1)
    keep_boxes = nms_locality(polys, test_config['nms_thres'])
    keep_boxes = keep_boxes.reshape((-1, 4, 2))
    keep_boxes, scores = reselect_box(
        keep_boxes, pred_pss, thres=test_config['reselect_thres'])

    resized_boxes = keep_boxes
    if len(keep_boxes) != 0:
        keep_boxes[:, :, 0] *= scale_w
        keep_boxes[:, :, 1] *= scale_h
    new_boxes = keep_boxes
    img, pss_img = vis_pss_map(imgs[0], pred_pss[0], h, w)
    tm, rm, bm, lm = vis_geo_map(img, pred_geo[0], h, w)
    box_img = vis_boxes(img, new_boxes)
    new_in = vis_multi_image(
        [img, pss_img, box_img, img, tm, rm, bm, lm], [2, -1])
    epoch_num = test_config['model'].split('_')[-2]
    image_name = img_name
    res_path, zip_path = save_result(image_name, new_in, new_boxes, epoch_num, test_config['outputs'],
                                     test_config['test_size'], test_config['nms_thres'],
                                     test_config['reselect_thres'])

    im = (norm(imgs[0].data.cpu()).numpy() *
          255).astype(np.uint8).transpose((1, 2, 0))
    img = Image.fromarray(im).convert('RGB').resize((w, h))
    image_np = np.array(img)
    # print(new_boxes)
    crop_images = rotate.rotate_img(new_boxes, image_np)

    # recognition
    crnn_model_path = 'crnn_package/weights/crnn_Rec_done_17_16549.pth'
    alphabet = alphabets.alphabet
    nclass = len(alphabet) + 1
    model = crnn.CRNN(32, 1, nclass, 256)
    if torch.cuda.is_available():
        model = model.cuda()
    print('loading pretrained model from {0}'.format(crnn_model_path))
    # 导入已经训练好的crnn模型
    model.load_state_dict(torch.load(crnn_model_path))
    result = {}
    result['name'] = img_name
    result['res_path'] = './photo/processed/'+img_name+'.jpg'
    text_temp = ''
    started = time.time()
    for i in range(len(crop_images)):
        image = Image.fromarray(crop_images[i])
        ww, hh = image.size
        new_ww = 250
        new_hh = int(new_ww / 250 * hh)
        image = image.resize((new_ww, new_hh))
        text_temp = text_temp+crnn_recognition(image, model)+';'
    finished = time.time()
    print('cost time: {0}'.format(finished - started))
    result['text'] = text_temp
    result['target'] = 'live'
    result['msg'] = getMsg(result['text'])
    print(result['text'])
    return result


def getMsg(text):
    # for i in dp_json:
    #     if i['商家名称'] in text or text in i['商家名称']:
    #         return i['商家名称']+','+str(i['评分'])+',人均消费:'+i['人均消费']+',评论数:'+str(i['评论数'])
     return '哈尔滨饺子馆,准四星商户,人均消费69.9元,评论数257条，值得推荐'


if __name__ == '__main__':
    test_rects('1', '', '')
