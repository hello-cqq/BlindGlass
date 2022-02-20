from .resnet import resnet18, resnet34, resnet50,resnet101, resnet152
import torch
import torch.nn as nn
import numpy as np
max_size = 640
def conv1x1(in_planes, out_planes, stride=1, has_bias=False):
    "1x1 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride,
                     padding=0, bias=has_bias)
def conv1x1_sigmoid(in_planes, out_planes, stride=1):
    return nn.Sequential(
            conv1x1(in_planes, out_planes, stride),
            nn.Sigmoid(),
            )
def conv1x1_bn_relu(in_planes, out_planes, stride=1):
    return nn.Sequential(
            conv1x1(in_planes, out_planes, stride),
            nn.BatchNorm2d(out_planes),
            nn.ReLU(inplace=True),
            )
def conv3x3(in_planes, out_planes, stride=1, has_bias=False):
    "3x3 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=has_bias)
def conv3x3_bn_relu(in_planes, out_planes, stride=1):
	return nn.Sequential(
	        conv3x3(in_planes, out_planes, stride),
	        nn.BatchNorm2d(out_planes),
	        nn.ReLU(inplace=True),
	        )
class Detect(nn.Module):
	def __init__(self, backbone):
		super(Detect, self).__init__()
		self.backbone = eval(backbone)(pretrained=True)
		self.deconv5 = nn.Sequential(
			conv1x1_bn_relu(2048,1024),
			conv3x3_bn_relu(1024,1024),
			nn.Upsample(scale_factor=2, mode='bilinear',align_corners=True))
		self.deconv4 = nn.Sequential(
			conv1x1_bn_relu(2048,512),
			conv3x3_bn_relu(512,512),
			nn.Upsample(scale_factor=2, mode='bilinear',align_corners=True))
		self.deconv3 = nn.Sequential(
			conv1x1_bn_relu(1024,256),
			conv3x3_bn_relu(256,256),
			nn.Upsample(scale_factor=2, mode='bilinear',align_corners=True))
		self.pss_map = conv1x1_sigmoid(512, 1)
		self.geo_map = conv1x1_sigmoid(512, 4)
		self.agl_map = conv1x1_sigmoid(512, 1)
	def forward(self, imgs):
		c2, c3, c4, c5 = self.backbone(imgs)
		out4 = torch.cat((self.deconv5(c5) ,c4), 1)
		out3 = torch.cat((self.deconv4(out4), c3),1)
		out2 = torch.cat((self.deconv3(out3), c2),1)
		pss_map = self.pss_map(out2)
		geo_map = self.geo_map(out2) * 640
		agl_map = (self.agl_map(out2) - 0.5) * np.pi/2
		return pss_map, geo_map, agl_map
# (scale_factor_w, scale_factor_h)=(1,1)


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
    cos_map = torch.cos(agl_map).repeat(1,4,1,1) #b,4,h,w
    sin_map = torch.sin(agl_map).repeat(1,4,1,1) #b,4,h,w
    rotated_points[:,:,0,:,:] = points[:,:,0,:,:] * cos_map + points[:,:,1,:,:] * sin_map + x_axis
    rotated_points[:,:,1,:,:] = points[:,:,1,:,:] * cos_map - points[:,:,0,:,:] * sin_map + y_axis
    rotated_points = rotated_points.permute((0,3,4,1,2))
    return rotated_points
def smoothed_l1_loss(pred_poi, true_poi, pss_map):
	b,h,w,four,two = pred_poi.shape
	pred_poi = pred_poi.view((b,h,w,8))
	true_poi = true_poi.view((b,h,w,8))
	loss = torch.nn.functional.smooth_l1_loss(pred_poi/max_size, true_poi/max_size, reduction ='none')
	loss = loss.mean(dim=-1).view((b,1,h,w))
	loss = loss * pss_map
	pss_map = pss_map.view((b, -1))
	loss = loss.view((b, -1))
	mean_loss = torch.sum(loss, dim=1)/(torch.sum(pss_map, dim=1)+1)
	return torch.mean(mean_loss)
def dice_loss(pred_pss, true_pss, training_mask):
	eps = 1e-5
	training_mask = training_mask.type_as(pred_pss)
	pred_pss = pred_pss.view_as(true_pss)
	intersection = torch.sum(true_pss * pred_pss * training_mask, (3,2,1))
	union = torch.sum(true_pss * training_mask, (3,2,1)) + torch.sum(pred_pss * training_mask, (3,2,1)) + eps
	loss = 1. - (2 * intersection/union)
	loss = torch.mean(loss)
	return loss
def iou_loss(pred_geo, true_geo):
	pred_t, pred_r, pred_b, pred_l = torch.split(pred_geo,1,dim=1)
	true_t, true_r, true_b, true_l = torch.split(true_geo,1,dim=1)

	pred_area = (pred_t + pred_b) * (pred_l + pred_r)
	true_area = (true_t + true_b) * (true_l + true_r)

	min_h = torch.min(pred_t, true_t) + torch.min(pred_b, true_b)
	min_w = torch.min(pred_l, true_l) + torch.min(pred_r, true_r)
	insection = min_h * min_w
	union = pred_area + true_area - insection
	iou = (insection + 1.0)/(union + 1.0)

	loss = -torch.log(iou)

	return loss
def agl_loss(pred_agl, true_agl):
	return (1. - torch.cos(pred_agl - true_agl))
def reg_loss(pred_geo, pred_agl, true_geo, true_agl):
	iou_ = iou_loss(pred_geo, true_geo)
	agl_ = agl_loss(pred_agl, true_agl)
	return iou_ + 10*agl_
def pss_loss(pred_pss, true_pss):
	eps = 1e-5
	loss = -(true_pss*torch.log(pred_pss + eps) + (1-true_pss)*torch.log(1 - pred_pss + eps))
	return loss
def ohem_reg(pred_geo, pred_agl, true_geo, true_agl, positive_mask):
	total_loss = reg_loss(pred_geo, pred_agl, true_geo, true_agl, positive_mask)
	batch_size = total_loss.size(0)
	geo_loss = []
	for idx in range(batch_size):
		if torch.sum(positive_mask[idx].view(-1)) == 0:
			geo_loss.append(torch.mean(total_loss[idx]*positive_mask[idx].type_as(total_loss)))
			continue
		if torch.sum(positive_mask[idx].view(-1)) < 128:
			geo_loss.append(torch.mean(torch.masked_select(total_loss[idx],positive_mask[idx])))
		else:
			positive_loss = torch.masked_select(total_loss[idx],positive_mask[idx])
			hard_positive_value,hard_positive_index = torch.topk(positive_loss.view(-1), 128)
			rand_idx = torch.randint(0,positive_loss.view(-1).size(0),(128,)).long()
			if isinstance(positive_loss, torch.cuda.FloatTensor):
				rand_idx = rand_idx.cuda()
			rand_positive_value = torch.index_select(positive_loss.view(-1),0,rand_idx)
			temp = torch.mean(hard_positive_value)*0.5 + torch.mean(rand_positive_value)*0.5
			geo_loss.append(temp)

	geo_loss = torch.stack(geo_loss)
	mean_loss = torch.mean(geo_loss)
	return mean_loss
def ohem_pss(pred_pss, true_pss, positive_mask, negetive_mask):
	total_loss = pss_loss(pred_pss, true_pss)
	batch_size = total_loss.size(0)
	pss_loss_ = []
	for idx in range(batch_size):
		positive_loss = torch.masked_select(total_loss[idx],positive_mask[idx])
		negetive_loss = torch.masked_select(total_loss[idx],negetive_mask[idx])
		hard_negetive_value,hard_negetive_index = torch.topk(negetive_loss.view(-1), 512)
		rand_idx = torch.randint(0,negetive_loss.view(-1).size(0),(512,)).long()
		if isinstance(positive_loss, torch.cuda.FloatTensor):
			rand_idx = rand_idx.cuda()
		rand_negetive_value = torch.index_select(negetive_loss.view(-1),0,rand_idx)
		selected_loss = torch.cat((positive_loss, hard_negetive_value, rand_negetive_value))
		pss_loss_.append(torch.mean(selected_loss))
	pss_loss_ = torch.stack(pss_loss_)
	mean_loss = torch.mean(pss_loss_)
	return mean_loss
# def ohem(pred, true):
def east_reg(pred_geo, pred_agl, true_geo, true_agl, positive_mask):
	total_loss = reg_loss(pred_geo, pred_agl, true_geo, true_agl)
	geo_loss = total_loss * positive_mask.type_as(total_loss)
	mean_loss = torch.mean(geo_loss)
	return mean_loss
def detect_loss(pred_pss, pred_geo, pred_agl, true_pss, true_geo, true_agl, training_mask):
	positive_mask = true_pss.type_as(training_mask) * training_mask
	negetive_mask = (1-true_pss.type_as(training_mask)) * training_mask
	#geo_loss = ohem_reg(pred_geo, pred_agl, true_geo, true_agl, positive_mask)
	geo_loss = east_reg(pred_geo, pred_agl, true_geo, true_agl, positive_mask)
	#pss_loss = ohem_pss(pred_pss, true_pss, positive_mask, negetive_mask)
	pss_loss = dice_loss(pred_pss, true_pss, training_mask)
	geo_loss *= 30
	total_loss = geo_loss + pss_loss
	return total_loss, geo_loss, pss_loss
def main():
	imgs = torch.ones([1,3,640,640])

	net = Detect('resnet50')
	pss_map, geo_map, agl_map = net(imgs)
	true_agl = torch.ones([1,1,160,160])
	true_geo = torch.ones([1,4,160,160])
	loss = reg_loss(geo_map, agl_map, true_geo, true_agl)
	print (loss.shape)
if __name__ == '__main__':
	main()
