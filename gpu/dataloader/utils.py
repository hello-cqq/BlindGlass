import os
import numpy as np
import math
import cv2
from shapely.geometry import Polygon
from PIL import Image, ImageDraw
import random
# from geo_map_cython_lib import gen_geo_map
import torch
def polygon_area(poly):
    '''
    compute area of a polygon
    :param poly:
    :return:
    '''
    edge = [
        (poly[1][0] - poly[0][0]) * (poly[1][1] + poly[0][1]),
        (poly[2][0] - poly[1][0]) * (poly[2][1] + poly[1][1]),
        (poly[3][0] - poly[2][0]) * (poly[3][1] + poly[2][1]),
        (poly[0][0] - poly[3][0]) * (poly[0][1] + poly[3][1])
    ]
    return np.sum(edge)/2.
def check_and_validate_polys(polys, tags, xxx_todo_changeme):
    '''
    check so that the text poly is in the same direction,
    and also filter some invalid polygons
    :param polys:
    :param tags:
    :return:
    '''
    (h, w) = xxx_todo_changeme
    if polys.shape[0] == 0:
        return polys
    polys[:, :, 0] = np.clip(polys[:, :, 0], 0, w-1)
    polys[:, :, 1] = np.clip(polys[:, :, 1], 0, h-1)

    validated_polys = []
    validated_tags = []
    for poly, tag in zip(polys, tags):
        p_area = polygon_area(poly)
        if abs(p_area) < 1:
            # print poly
            #print('invalid poly')
            continue
        if p_area > 0:
            #continue

            #print('poly in wrong direction')
            if poly[0][0] < poly[1][0]:
                poly = poly[(3, 2, 1, 0), :]

            elif poly[0][0] > poly[1][0]:
                poly = poly[(1, 0, 3, 2), :]

            else:
                continue

        validated_polys.append(poly)
        validated_tags.append(tag)
    return np.array(validated_polys), np.array(validated_tags)


def shrink(poly):
    def move_point_to_another_point_a_ratio_length(point_s, point_d, ratio):
        return ratio * point_d + ( 1- ratio)*point_s

    length = [None, None, None, None]#[top, right, bottom, left]
    for i in range(4):
        length[i] = np.linalg.norm(poly[i] - poly[(i + 1) % 4])

    short = [None, None, None, None]#[tl, tr, br, bl]
    for i in range(4):
        short[i] = min(length[i],length[i-1])

    k = 0.3
    poly_1 = np.zeros_like(poly)
    poly_1[0] = move_point_to_another_point_a_ratio_length(poly[0], poly[1], k*short[0]/length[0])
    poly_1[1] = move_point_to_another_point_a_ratio_length(poly[1], poly[0], k*short[1]/length[0])
    poly_1[2] = move_point_to_another_point_a_ratio_length(poly[2], poly[3], k*short[2]/length[2])
    poly_1[3] = move_point_to_another_point_a_ratio_length(poly[3], poly[2], k*short[3]/length[2])

    poly_2 = np.zeros_like(poly)
    poly_2[0] = move_point_to_another_point_a_ratio_length(poly_1[0], poly_1[3], k*short[0]/length[3])
    poly_2[1] = move_point_to_another_point_a_ratio_length(poly_1[1], poly_1[2], k*short[1]/length[1])
    poly_2[2] = move_point_to_another_point_a_ratio_length(poly_1[2], poly_1[1], k*short[2]/length[1])
    poly_2[3] = move_point_to_another_point_a_ratio_length(poly_1[3], poly_1[0], k*short[3]/length[3])

    return poly_2
def sort_angle(poly):#(4,2)
    # p_lowest = np.argmax(poly[:,1])
    # if np.count_nonzero(poly[:, 1] == poly[p_lowest, 1]) == 2:
    #   return 0
    # p_lowest_right = (p_lowest - 1) % 4
    # p_lowest_left = (p_lowest + 1) % 4
    # angle = np.arctan(-(poly[p_lowest][1] - poly[p_lowest_right][1])*1.0/(poly[p_lowest][0] - poly[p_lowest_right][0]))
    # print p_lowest_right, p_lowest_left
    # print poly
    tl_p, tr_p, br_p, bl_p = poly
    angle1 = np.arctan(-(br_p[1] - bl_p[1])*1.0/(br_p[0] - bl_p[0]))
    # print poly
    return angle1
def point_dist_to_line(p1,p2,p3):
  #line:p1,p2   point:p3
    dist = np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)
    return dist
def get_mini_boxes(cnt):
    #print(cnt)
    bounding_box = cv2.minAreaRect(cnt)
    points = cv2.boxPoints(bounding_box)
    points = list(points)
    ps = sorted(points,key = lambda x:x[0])

    if ps[1][1] > ps[0][1]:
        px1 = ps[0][0]
        py1 = ps[0][1]
        px4 = ps[1][0]
        py4 = ps[1][1]
    else:
        px1 = ps[1][0]
        py1 = ps[1][1]
        px4 = ps[0][0]
        py4 = ps[0][1]
    if ps[3][1] > ps[2][1]:
        px2 = ps[2][0]
        py2 = ps[2][1]
        px3 = ps[3][0]
        py3 = ps[3][1]
    else:
        px2 = ps[3][0]
        py2 = ps[3][1]
        px3 = ps[2][0]
        py3 = ps[2][1]

    return np.array([[px1, py1], [px2, py2], [px3, py3], [px4, py4]])
def generate_gt(h, w, boxes, tags, min_text_size=5):
    h, w = (h, w)
    text_polys, text_tags = check_and_validate_polys(boxes, tags, (h,w))
    idx_maps = np.zeros((h, w), dtype=np.uint8)
    pss_maps = np.zeros((1,h, w), dtype=np.uint8)
    agl_maps = np.zeros((1,h,w), dtype=np.float32)
    geo_maps = np.zeros((4,h,w), dtype=np.float32)
    training_mask = np.ones((1,h,w), dtype=np.uint8)
    areas = []

    if text_polys.shape[0] > 0:
      for poly_idx, poly_tag in enumerate(zip(text_polys, text_tags)):
          poly = poly_tag[0]
          text  = poly_tag[1]
          poly_h = min(np.linalg.norm(poly[0] - poly[3]), np.linalg.norm(poly[1] - poly[2]))
          poly_w = min(np.linalg.norm(poly[0] - poly[1]), np.linalg.norm(poly[2] - poly[3]))
          if min(poly_w, poly_h) < min_text_size or text=='###':
              cv2.fillPoly(training_mask[0], poly.astype(np.int32)[np.newaxis, :, :], 0)
          else:
              box = get_mini_boxes(poly)
              [tl_p, tr_p, br_p, bl_p] = box
              cv2.fillPoly(training_mask[0], box.astype(np.int32)[np.newaxis, :, :], 0)
              shrinked_box = shrink(box)
              cv2.fillPoly(idx_maps, shrinked_box.astype(np.int32)[np.newaxis, :, :], poly_idx+1)
              cv2.fillPoly(training_mask[0], shrinked_box.astype(np.int32)[np.newaxis, :, :], 1)
              cv2.fillPoly(pss_maps[0], shrinked_box.astype(np.int32)[np.newaxis, :, :], 1)
              angle = sort_angle(box)
              cv2.fillPoly(agl_maps[0], shrinked_box.astype(np.int32)[np.newaxis, :, :], angle)

              xy_in_poly = np.argwhere(idx_maps == (poly_idx + 1))
              gen_geo_map.gen_geo_map(geo_maps, xy_in_poly, box)
              #for y, x in xy_in_poly:
                  #point = np.array([x, y], dtype=np.float32)
                  #geo_maps[0,y,x] = point_dist_to_line(tl_p, tr_p, point)#/np.linalg.norm(tl_p - bl_p)
                  #geo_maps[1,y,x] = point_dist_to_line(tr_p, br_p, point)#/np.linalg.norm(tl_p - tr_p)
                  #geo_maps[2,y,x] = point_dist_to_line(br_p, bl_p, point)#/np.linalg.norm(tl_p - bl_p)
                  #geo_maps[3,y,x] = point_dist_to_line(bl_p, tl_p, point)#/np.linalg.norm(tl_p - tr_p)
    return pss_maps,geo_maps,agl_maps,training_mask#, text_polys, text_tags
def ploy_nms(boxes, scores, thresh):
    ploys = [Polygon(x) for x in boxes]
    areas = [x.area for x in ploys]
    order = np.array(scores).argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        ious = []
        for j in order[1:]:
            inter = ploys[i].intersection(ploys[j]).area
            ious.append(inter/(ploys[i].area + ploys[j].area - inter))
        inds = np.where(np.array(ious) <= thresh)[0]
        order = order[inds + 1]
    return keep
def intersection(g, p):
    g = Polygon(g[:8].reshape((4, 2)))
    p = Polygon(p[:8].reshape((4, 2)))
    if not g.is_valid or not p.is_valid:
        return 0
    inter = Polygon(g).intersection(Polygon(p)).area
    union = g.area + p.area - inter
    if union == 0:
        return 0
    else:
        return inter/union


def weighted_merge(g, p):
    g[:8] = (g[8] * g[:8] + p[8] * p[:8])/(g[8] + p[8])
    g[8] = (g[8] + p[8])
    return g


def standard_nms(S, thres):
    order = np.argsort(S[:, 8])[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        ovr = np.array([intersection(S[i], S[t]) for t in order[1:]])

        inds = np.where(ovr <= thres)[0]
        order = order[inds+1]

    return S[keep][:,:8]


def nms_locality(polys, thres=0.3):
    '''
    locality aware nms of EAST
    :param polys: a N*9 numpy array. first 8 coordinates, then prob
    :return: boxes after nms
    '''
    S = []
    p = None
    for g in polys:
        if p is not None and intersection(g, p) > thres:
            p = weighted_merge(g, p)
        else:
            if p is not None:
                S.append(p)
            p = g
    if p is not None:
        S.append(p)

    if len(S) == 0:
        return np.array([])
    return standard_nms(np.array(S), thres)
def reselect_box(boxes, pss_maps,scale_factor=(0.25, 0.25), thres = 0.3):
    b, c, h, w = pss_maps.shape
    pss_maps_numpy = pss_maps.data.cpu().numpy()
    scale_h , scale_w = scale_factor
    boxes[:,:,0] *= scale_w
    boxes[:,:,1] *= scale_h
    new_boxes = []
    keep = []
    for idx, box in enumerate(boxes):
        maps = np.zeros((h,w), dtype=np.float32)
        cv2.fillPoly(maps, box.astype(np.int32)[np.newaxis, :, :], 1)
        mean = np.sum(maps * pss_maps_numpy[0,0,:,:]) *1.0 / np.sum(maps)
        if mean > thres:
            new_boxes.append(box)
            keep.append(idx)
    boxes[:,:,0] /= scale_w
    boxes[:,:,1] /= scale_h
    return np.array(new_boxes), np.array(keep)
def restore_box(pss_map, geo_maps, agl_map, scale_factor = 1):
    h, w = pss_map.shape
    x_axis = np.tile(np.arange(w).reshape(1,w),(h,1)) * scale_factor
    y_axis = np.tile(np.arange(h).reshape(h,1),(1,w)) * scale_factor
    ts, rs, bs, ls = geo_maps*pss_map
    points = np.zeros([h, w, 4, 2])
    points[:,:,0,0] =  - ls
    points[:,:,0,1] =  - ts
    points[:,:,1,0] =  + rs
    points[:,:,1,1] =  - ts
    points[:,:,2,0] =  + rs
    points[:,:,2,1] =  + bs
    points[:,:,3,0] =  - ls
    points[:,:,3,1] =  + bs
    rotated_points = np.zeros_like(points)
    cos_map = np.cos(agl_map)
    sin_map = np.sin(agl_map)
    points = np.transpose(points, [2,0,1,3])
    rotated_points = np.transpose(rotated_points, [2,0,1,3])
    rotated_points[:,:,:,0] = points[:,:,:,0] * cos_map + points[:,:,:,1] * sin_map + x_axis
    rotated_points[:,:,:,1] = points[:,:,:,1] * cos_map - points[:,:,:,0] * sin_map + y_axis
    rotated_points = np.transpose(rotated_points, [1,2,0,3])
    index = np.where(pss_map>0.5)
    selected_boxes = rotated_points[index]
    selected_scores = pss_map[index]
    keep_index =  ploy_nms(selected_boxes, selected_scores, 0.5)
    keep_boxes = selected_boxes[keep_index]
    return keep_boxes
def restore_box_gpu(pss_map, geo_maps, agl_map, scale_factor_w=1, scale_factor_h=1):
    b,c,h,w = pss_map.shape
    x_axis = torch.arange(w).view(1,w).repeat(h,1).type_as(pss_map)*scale_factor_w
    y_axis = torch.arange(h).view(h,1).repeat(1,w).type_as(pss_map)*scale_factor_h
    ts, rs, bs, ls = [v.squeeze(1) for v in list(torch.split(geo_maps, 1, dim=1))]
    points = torch.zeros([b,4,2,h,w]).type_as(pss_map)
    points[:,0,0,:,:] -=  ls
    points[:,0,1,:,:] -=  ts
    points[:,1,0,:,:] +=  rs
    points[:,1,1,:,:] -=  ts
    points[:,2,0,:,:] +=  rs
    points[:,2,1,:,:] +=  bs
    points[:,3,0,:,:] -=  ls
    points[:,3,1,:,:] +=  bs
    rotated_points = torch.zeros([b,4,2,h,w]).type_as(pss_map)
    cos_map = torch.cos(agl_map).squeeze(1) #b,h,w
    sin_map = torch.sin(agl_map).squeeze(1) #b,h,w
    rotated_points[:,:,0,:,:] = points[:,:,0,:,:] * cos_map + points[:,:,1,:,:] * sin_map + x_axis
    rotated_points[:,:,1,:,:] = points[:,:,1,:,:] * cos_map - points[:,:,0,:,:] * sin_map + y_axis

    masks = pss_map.ge(0.5).view(b,1,1,h,w).repeat(1,4,2,1,1) #b,..,h,w

    selected_boxes = []
    selected_scores= []
    for idx in range(b):
        mask = masks[idx] #4,2,h,w
        all_points = rotated_points[idx] #4,2,h,w
        all_scores = pss_map[idx].squeeze(0) #h,w
        if torch.sum(mask) == 0:
            selected_boxes.append([])
            selected_scores.append([])
        else:
            selected = torch.masked_select(all_points, mask).view(4,2,-1).permute(2,0,1)
            scores   = torch.masked_select(all_scores, mask[0][0])
            selected_scores.append(scores.data.cpu().numpy())
            selected_boxes.append(selected.data.cpu().numpy())
    return np.array(selected_boxes), np.array(selected_scores)

def restore_box_gpu2(pss_map, geo_maps, agl_map, scale_factor_w=1, scale_factor_h=1):
    b,c,h,w = pss_map.shape
    x_axis = torch.arange(w).view(1,w).repeat(h,1).type_as(pss_map)*scale_factor_w
    y_axis = torch.arange(h).view(h,1).repeat(1,w).type_as(pss_map)*scale_factor_h
    ts, rs, bs, ls = [v.squeeze(1) for v in list(torch.split(geo_maps, 1, dim=1))]
    points = torch.zeros([b,4,2,h,w]).type_as(pss_map)
    points[:,0,0,:,:] -=  ls
    points[:,0,1,:,:] -=  ts
    points[:,1,0,:,:] +=  rs
    points[:,1,1,:,:] -=  ts
    points[:,2,0,:,:] +=  rs
    points[:,2,1,:,:] +=  bs
    points[:,3,0,:,:] -=  ls
    points[:,3,1,:,:] +=  bs
    rotated_points = torch.zeros([b,4,2,h,w]).type_as(pss_map)
    cos_map = torch.cos(agl_map).squeeze(1) #b,h,w
    sin_map = torch.sin(agl_map).squeeze(1) #b,h,w
    rotated_points[:,:,0,:,:] = points[:,:,0,:,:] * cos_map + points[:,:,1,:,:] * sin_map + x_axis
    rotated_points[:,:,1,:,:] = points[:,:,1,:,:] * cos_map - points[:,:,0,:,:] * sin_map + y_axis

    masks = pss_map.ge(0.5).view(b,1,1,h,w).repeat(1,4,2,1,1) #b,..,h,w

    selected_boxes = []
    selected_scores= []
    selected_cos = []
    selected_sin = []
    for idx in range(b):
        mask = masks[idx] #4,2,h,w
        all_points = rotated_points[idx] #4,2,h,w
        all_scores = pss_map[idx].squeeze(0) #h,w
        if torch.sum(mask) == 0:
            selected_boxes.append([])
            selected_scores.append([])
        else:
            selected = torch.masked_select(all_points, mask).view(4,2,-1).permute(2,0,1)
            scores   = torch.masked_select(all_scores, mask[0][0])
            cos     = torch.masked_select(cos_map[idx], mask[0][0])
            sin     = torch.masked_select(sin_map[idx], mask[0][0])
            selected_scores.append(scores)
            selected_boxes.append(selected)
            selected_cos.append(cos)
            selected_sin.append(sin)
    return selected_boxes, selected_scores, selected_cos. selected_sin


def restore_points_geo(pss_map, geo_maps, agl_map, scale_factor_w=2, scale_factor_h=2):
    b,c,h,w = pss_map.shape
    x_axis = torch.arange(w).view(1,w).repeat(h,1).type_as(pss_map)*scale_factor_w
    y_axis = torch.arange(h).view(h,1).repeat(1,w).type_as(pss_map)*scale_factor_h
    ts, rs, bs, ls = [v.squeeze(1) for v in list(torch.split(geo_maps, 1, dim=1))]
    points = torch.zeros([b,4,2,h,w]).type_as(pss_map)
    points[:,0,0,:,:] -=  ls
    points[:,0,1,:,:] -=  ts
    points[:,1,0,:,:] +=  rs
    points[:,1,1,:,:] -=  ts
    points[:,2,0,:,:] +=  rs
    points[:,2,1,:,:] +=  bs
    points[:,3,0,:,:] -=  ls
    points[:,3,1,:,:] +=  bs
    rotated_points = torch.zeros([b,4,2,h,w]).type_as(pss_map)
    cos_map = torch.cos(agl_map).squeeze(1) #b,h,w
    sin_map = torch.sin(agl_map).squeeze(1) #b,h,w
    rotated_points[:,:,0,:,:] = points[:,:,0,:,:] * cos_map + points[:,:,1,:,:] * sin_map + x_axis
    rotated_points[:,:,1,:,:] = points[:,:,1,:,:] * cos_map - points[:,:,0,:,:] * sin_map + y_axis

    #masks = pss_map.ge(0.5).view(b,1,1,h,w).repeat(1,4,2,1,1) #b,..,h,w

    for idx in range(b):
        all_points = rotated_points[idx] #4,2,h,w
    return all_points.data.cpu().numpy()

