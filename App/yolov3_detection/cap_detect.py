# -*- coding: utf-8 -*-


from .detect import detect_cv2
from .darknet import Darknet
import cv2
import os


class YoloDetect():
    def __init__(self, GPU_ids=0):
        self.cfgfile = './App/yolov3_detection/yolov3.cfg'
        self.weightfile = './App/yolov3_detection/yolov3.weights'

        self.model = Darknet(self.cfgfile)
        self.model.load_weights(self.weightfile)
        self.num_classes = 80

        if self.num_classes == 20:
            self.namesfile = './App/yolov3_detection/voc.names'
        elif self.num_classes == 80:
            self.namesfile = './App/yolov3_detection/coco.names'
        else:
            self.namesfile = './App/yolov3_detection/names'

        os.environ["CUDA_VISIBLE_DEVICES"] = str(GPU_ids)   # 指定GPU

    def detection(self, frame):
        return detect_cv2(self.model, self.cfgfile, self.weightfile, frame)

if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    YOLOV3 = YoloDetect(GPU_ids=0)   # 实例化YOLOV3检测

    while True:
        ret, frame = cap.read()
        imgx = YOLOV3.detection(frame)
        cv2.imshow('frame', imgx)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

