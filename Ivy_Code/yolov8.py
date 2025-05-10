from ultralytics import YOLO
import torch
import random

class Yolov8():
    def __init__(self):
        self.model = YOLO("/home/pi/Ivy/model/yolov8n_ncnn_model")

    def detect(self, frame, iou = 0.4, conf = 0.4):
        results = self.model(frame, iou = iou, conf = conf, verbose = False)
        
        img = results[0].plot()
        predict = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                p1 = [x1, y1]
                p2 = [x2, y1]
                p3 = [x2, y2]
                p4 = [x1, y2]

                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                predict.append([class_name, [p1, p2, p3, p4]])
        
        return predict, img