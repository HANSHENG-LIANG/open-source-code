import os
# os.chdir("..")
from copy import deepcopy

import torch
import cv2
import numpy as np
import matplotlib.cm as cm
from src.utils.plotting import make_matching_figure

from src.loftr import LoFTR, default_cfg

import pdb
# The default config uses dual-softmax.
# The outdoor and indoor models share the same config.
# You can change the default values like thr and coarse_match_type.

_default_cfg = deepcopy(default_cfg)
_default_cfg['coarse']['temp_bug_fix'] = True  # set to False when using the old ckpt
matcher = LoFTR(config=_default_cfg) # init model 
matcher.load_state_dict(torch.load("weights/indoor_ds_new.ckpt")['state_dict']) # load pretrain model "benchmark"
matcher = matcher.eval().cuda() # BN Dropout train/test

# Load example images
img0_pth = "assets/scannet_sample_images/scene0711_00_frame-001680.jpg"
img1_pth = "assets/scannet_sample_images/scene0711_00_frame-001995.jpg"
img0_raw = cv2.imread(img0_pth, cv2.IMREAD_GRAYSCALE) # (968, 1296)
img1_raw = cv2.imread(img1_pth, cv2.IMREAD_GRAYSCALE) # (968, 1296)
img0_raw = cv2.resize(img0_raw, (640, 480)) # (480, 640)
img1_raw = cv2.resize(img1_raw, (640, 480)) # (480, 640)

img0 = torch.from_numpy(img0_raw)[None][None].cuda() / 255. # numpy=>torch/tf/paddle
img1 = torch.from_numpy(img1_raw)[None][None].cuda() / 255. # [1, 1, 480, 640] => [bs, c, w, h]/ [bs, w, h, c]..
batch = {'image0': img0, 'image1': img1}

# Inference with LoFTR and get prediction
with torch.no_grad():
    # 2D matching task:
    # input: img1 [bs, c, w, h] & img2 [bs, c, w, h] ==> pred: img1 [num_point, 2] &  img2 [num_point, 2]
    matcher(batch)
    mkpts0 = batch['mkpts0_f'].cpu().numpy() # (338, 2)
    mkpts1 = batch['mkpts1_f'].cpu().numpy() # (338, 2)
    mconf = batch['mconf'].cpu().numpy() # (338,)
    
# Draw
color = cm.jet(mconf)
text = [
    'LoFTR',
    'Matches: {}'.format(len(mkpts0)),
]
fig = make_matching_figure(img0_raw, img1_raw, mkpts0, mkpts1, color, text=text, path="./demo1.jpg")


# outdoor example
from src.loftr import LoFTR, default_cfg

# The default config uses dual-softmax.
# The outdoor and indoor models share the same config.
# You can change the default values like thr and coarse_match_type.
matcher = LoFTR(config=default_cfg)
matcher.load_state_dict(torch.load("weights/outdoor_ds.ckpt")['state_dict'])
matcher = matcher.eval().cuda()

default_cfg['coarse']

# Load example images
img0_pth = "assets/phototourism_sample_images/united_states_capitol_26757027_6717084061.jpg"
img1_pth = "assets/phototourism_sample_images/united_states_capitol_98169888_3347710852.jpg"
img0_raw = cv2.imread(img0_pth, cv2.IMREAD_GRAYSCALE)
img1_raw = cv2.imread(img1_pth, cv2.IMREAD_GRAYSCALE)
img0_raw = cv2.resize(img0_raw, (img0_raw.shape[1]//8*8, img0_raw.shape[0]//8*8))  # input size shuold be divisible by 8
img1_raw = cv2.resize(img1_raw, (img1_raw.shape[1]//8*8, img1_raw.shape[0]//8*8))

img0 = torch.from_numpy(img0_raw)[None][None].cuda() / 255.
img1 = torch.from_numpy(img1_raw)[None][None].cuda() / 255.
batch = {'image0': img0, 'image1': img1}

# Inference with LoFTR and get prediction
with torch.no_grad():
    matcher(batch)
    mkpts0 = batch['mkpts0_f'].cpu().numpy()
    mkpts1 = batch['mkpts1_f'].cpu().numpy()
    mconf = batch['mconf'].cpu().numpy()
    

# Draw
color = cm.jet(mconf)
text = [
    'LoFTR',
    'Matches: {}'.format(len(mkpts0)),
]
fig = make_matching_figure(img0_raw, img1_raw, mkpts0, mkpts1, color, text=text, path="./demo2.jpg")

