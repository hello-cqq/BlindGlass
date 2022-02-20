import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread, imresize
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
import cv2
def sort_angle(poly):#(4,2)
    tl_p, tr_p, br_p, bl_p = poly
    angle1 = np.arctan(-(br_p[1] - bl_p[1])*1.0/(br_p[0] - bl_p[0]))
    return angle1
def point_dist_to_line(p1,p2,p3):
  #line:p1,p2   point:p3
    dist = np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)
    return dist
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
def get_mini_boxes(cnt):
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
def generate_gt(img, boxes):
	h,w,_ = img.shape
	pss_map = np.zeros([h,w])
	geo_maps = np.zeros([4,h,w])
	agl_map = np.zeros([h,w])
	for box in boxes:
		shrinked_box = shrink(box)
		cv2.fillPoly(pss_map, shrinked_box.astype(np.int32)[np.newaxis, :, :], 1)
		angle = sort_angle(box)
		cv2.fillPoly(agl_map, box.astype(np.int32)[np.newaxis, :, :], angle)
		[tl_p, tr_p, br_p, bl_p] = box
		xy_in_poly = np.argwhere(pss_map == 1)
		for y, x in xy_in_poly:
			point = np.array([x, y], dtype=np.float32)
			geo_maps[0,y,x]=point_dist_to_line(tl_p, tr_p, point)
			geo_maps[1,y,x]=point_dist_to_line(tr_p, br_p, point)
			geo_maps[2,y,x]=point_dist_to_line(br_p, bl_p, point)
			geo_maps[3,y,x]=point_dist_to_line(bl_p, tl_p, point)
	return pss_map,geo_maps,agl_map
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

def restore_box(pss_map, geo_maps, agl_map, scale_factor = 1):
    h, w = pss_map.shape
    x_axis = np.tile(np.arange(w).reshape(1,w),(h,1)) * scale_factor
    y_axis = np.tile(np.arange(h).reshape(h,1),(1,w)) * scale_factor
    ts, rs, bs, ls = geo_maps
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
    points[:,:,:,0] = points[:,:,:,0] + x_axis
    points[:,:,:,1] = points[:,:,:,1] + y_axis
    rotated_points = np.transpose(rotated_points, [1,2,0,3])
    points = np.transpose(points, [1,2,0,3])
    index = np.where(pss_map>0.3)
    selected_boxes = rotated_points[index]
    selected_scores = pss_map[index]
    keep_index =  ploy_nms(selected_boxes, selected_scores, 0.5)
    keep_boxes = selected_boxes[keep_index]
    # print selected_boxes.shape
    # print keep_boxes.shape
    return keep_boxes
def show_image(image):
	plt.imshow(image)
	plt.show()
def main():
	image = np.zeros((720,1280,3)).astype(np.uint8)
	box_ = np.array([[[100,100],[300,80],[280,280],[80,300]]])
	box_[:,:,0] += 100
	box = []
	for b in box_:
		box.append(get_mini_boxes(b))
	box = np.array(box)
	pss_map,geo_maps,agl_map = generate_gt(image, box)
	boxes = restore_box(pss_map, geo_maps, agl_map, scale_factor = 1)
	img = Image.fromarray(image)
	img_draw = ImageDraw.Draw(img)
	for ind, poly in enumerate(box_):
	    img_draw.line([poly[0, 0], poly[0, 1], poly[1, 0], poly[1, 1], poly[2, 0], poly[2, 1], poly[3, 0], poly[3, 1], poly[0, 0], poly[0, 1]], width=4, fill=(0, 0, 255))

	for ind, poly in enumerate(box):
	    img_draw.line([poly[0, 0], poly[0, 1], poly[1, 0], poly[1, 1], poly[2, 0], poly[2, 1], poly[3, 0], poly[3, 1], poly[0, 0], poly[0, 1]], width=4, fill=(255, 0, 0))
	for ind, poly in enumerate(boxes):
	    img_draw.line([poly[0, 0], poly[0, 1], poly[1, 0], poly[1, 1], poly[2, 0], poly[2, 1], poly[3, 0], poly[3, 1], poly[0, 0], poly[0, 1]], width=4, fill=(0, 255, 0))
	    # break
	show_image(np.array(img))
	return 0
if __name__ == '__main__':
	main()