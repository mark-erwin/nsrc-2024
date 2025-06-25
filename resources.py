import cv2

cam = cv2.VideoCapture(0)
plate_model = 'resources/qatarlpr.onnx'
smoke_model = 'resources/smoke.onnx'
car_model = 'resources/yolov5s.onnx'
coco = 'resources/coco.txt'
registry = 'data/registry.json'
