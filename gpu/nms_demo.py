# coding=utf-8

from __future__ import division
import numpy as np
import tensorflow as tf
import cv2
from PIL import Image
import utils
import os
import time

# os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
'''
设置模型需要的图片长宽
'''
IMAGE_H, IMAGE_W = 416, 416
EPOCHS = 5
'''
读取检测类型
'''
classes = utils.read_coco_names('./data/coco.names')
'''
读取类别的数量
'''
num_classes = len(classes)
cpu_nms_graph, gpu_nms_graph = tf.Graph(), tf.Graph()
'''
cpu上读取模型
'''
input_tensor, output_tensors = utils.read_pb_return_tensors(gpu_nms_graph, "./yolov3_gpu_nms.pb",
                                                            ["Placeholder:0", "concat_10:0", "concat_11:0", "concat_12:0"])
# config = tf.ConfigProto(allow_soft_placement=True)
# config.gpu_options.allow_growth = True
# sess = tf.Session(graph=gpu_nms_graph,config=config)
sess = tf.Session(graph=gpu_nms_graph)
def shibie(img_name, img_path, location):
    '''
    红绿灯识别的入口函数
    Args:
        img_name:图片名字
        img_path:原图路径
        location：图片拍摄地点
    Returns:
        result:json字符串，包含图片的完整信息
    '''
    image_path = img_path
    #'./data/demo_data/street2.jpg'
    print(image_path)
    img = Image.open(image_path)
    img_resized = np.array(img.resize(size=(IMAGE_H, IMAGE_W)), dtype=np.float32)
    img_resized = img_resized / 255.
    
    result = {}
    result['name'] = img_name
    # with tf.Session(graph=gpu_nms_graph) as sess:
    #for i in range(EPOCHS):
    start = time.time()
    boxes, scores, labels = sess.run(output_tensors, feed_dict={input_tensor: np.expand_dims(img_resized, axis=0)})
#         boxes, scores, labels = utils.cpu_nms(boxes, scores, num_classes, score_thresh=0.5, iou_thresh=0.5)
#         print("=> nms on cpu the number of boxes= %d  time=%.2f ms" %(len(boxes), 1000*(time.time()-start)))
    #将label方框画在图片上
    image = utils.draw_boxes(img, boxes, scores, labels, classes, [IMAGE_H, IMAGE_W], show=False)
    result['res_path'] = './photo/processed/'+img_name+'.jpg'
    image.save(result['res_path'], quality=95)
    print(result['res_path'])
    # traffic light
    '''
    红绿灯识别模块
    '''
    detection_size, original_size = np.array([IMAGE_H, IMAGE_W]), np.array(img.size)
    ratio = original_size / detection_size
    lights_size = []
    lights_idx = []
    color = 'None'
    # if  labels==None:
    #     labels=np.array([])
    for j in range(len(labels)):  # for each bounding box, do:
        bbox, score, label = boxes[j], scores[j], classes[labels[j]]
        # convert_to_original_size
        bbox = list((bbox.reshape(2, 2) * ratio).reshape(-1))
        if label == 'traffic light':
            light_size = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            lights_idx.append(j)
            lights_size.append(light_size)

    if  len(lights_size) > 0:
        #找到面积最大的红绿灯
        max_idx = lights_idx[lights_size.index(max(lights_size))]
        #转换到原图尺寸
        bbox_light = boxes[max_idx]
        bbox_light = list((bbox_light.reshape(2, 2) * ratio).reshape(-1))
        xmin = int(bbox_light[0])
        ymin = int(bbox_light[1])
        xmax = int(bbox_light[2])
        ymax = int(bbox_light[3])
        image_light = cv2.imread(image_path)
        image_light = image_light[ymin:ymax, xmin:xmax]
        #image_light = cv2.resize(image_light, (20, 40), interpolation=cv2.INTER_CUBIC)
        histr_g = cv2.calcHist([image_light], [2], None, [256], [0, 256])
        if histr_g[-1] > 3:
            color = 'red'
        else:
            color = 'green'
        #cv2.imshow('light', image_light)
        #cv2.waitKey(0)

    # count
    # 计算检测到的车辆及行人的个数
    num_person = np.sum(labels == 0)
    num_bicycle = np.sum(labels == 1)
    num_car = np.sum(labels == 2)
    num_motorbike = np.sum(labels == 3)
    num_bus = np.sum(labels == 5)
    num_truck = np.sum(labels == 7)
    num_traffic = {'person': num_person, 'bicycle': num_bicycle, 'car': num_car, 'motorbike': num_motorbike,
                    'bus': num_bus, 'truck': num_truck, 'traffic light': color}
    
    result['text'] = '暂未识别'
    
    result['target'] = getTarget(num_traffic)
    result['msg'] = getMsg(num_traffic)
    end = time.time()
    print('gpu delay:',end-start)
    return result

def getTarget(num_traffic):
    '''
    通过识别结果返回固定格式的目标字符串
    '''
    reslut_str = ''
    for key ,value in num_traffic.items():
        if key!='traffic light' and value!=0:
            reslut_str = reslut_str+key+'-'+str(value)+';' 
    if num_traffic['traffic light'] == 'red':
        reslut_str = reslut_str + 'traffic light-'+'红灯'
    elif num_traffic['traffic light'] == 'green':
        reslut_str = reslut_str + 'traffic light-'+'绿灯'
    return reslut_str

def getMsg(num_traffic):
    '''
    对识别结果进行简单整合返回描述信息
    '''
    deng_str = ''
    che_str = ''
    ren_str = ''
    ches = num_traffic['bus'] + num_traffic['car']+ num_traffic['motorbike'] + num_traffic['bicycle'] + num_traffic['truck']
    rens = num_traffic['person']
    dengs = num_traffic['traffic light']
    if ches>10:
        che_str = '车流量较大'
    else:
        che_str = '车流量较小'
    if rens>10:
        ren_str = '人流量较大'
    else:
        ren_str = '人流量较小'
    
    if dengs=='red':
        deng_str = '现在是红灯'
        
    elif dengs=='green':
        deng_str = '现在是绿灯'
    else:
        deng_str = ''
    result_str = '你正处于红绿灯路口'+deng_str+','+che_str+','+ren_str+',请谨慎前行'
    print(result_str)
    
    return result_str
    

# shibie('0081','0081.jpg','earth')
# time.sleep(5)
# shibie('0081', '0081.jpg', 'earth')


