#coding: utf-8
import sys
import time
from PIL import Image, ImageDraw
from .tiny_yolo import TinyYoloNet
from .utils import *
from .darknet import Darknet
import cv2


def detect_cv2(model, cfgfile, weightfile, img):
    num_classes = 80
    if num_classes == 20:
        namesfile = './App/yolov3_detection/voc.names'
    elif num_classes == 80:
        namesfile = './App/yolov3_detection/coco.names'
    else:
        namesfile = './App/yolov3_detection/names'
    
    use_cuda = 1
    if use_cuda:
        model.cuda()

    sized = cv2.resize(img, (model.width, model.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)
    
    for i in range(1):
        start = time.time()
        boxes = do_detect(model, sized, 0.5, 0.4, use_cuda)
        finish = time.time()
        #if i == 1:
            #print('%s: Predicted in %f seconds.' % (imgfile, (finish-start)))
    #print('---------box num', len(boxes))
    class_names = load_class_names(namesfile)
    images=plot_boxes_cv2(img, boxes, savename='predictions.jpg', class_names=class_names)
    return images    

