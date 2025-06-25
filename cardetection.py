import cv2
import numpy as np

import platedetection
import resources

car_model = resources.car_model
net = cv2.dnn.readNetFromONNX(car_model)
coco = open(resources.coco, 'r')
classes = coco.read().split('\n')


def compute_iou(smoke_box, car_box):
    # Determine the (x, y)-coordinates of the intersection rectangle
    xA = max(smoke_box[0], car_box[0])
    yA = max(smoke_box[1], car_box[1])
    xB = min(smoke_box[0] + smoke_box[2], car_box[0] + car_box[2])
    yB = min(smoke_box[1] + smoke_box[3], car_box[1] + car_box[3])

    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # Compute the area of both the smoke and car rectangles
    smoke_area = smoke_box[2] * smoke_box[3]
    car_area = car_box[2] * car_box[3]

    # Compute the union area
    unionArea = smoke_area + car_area - interArea

    # Compute IoU
    iou = interArea / unionArea

    return iou


def detectCar(smoke_boxes, scans):
    frame = cv2.imread('./frames/smoke_detections/frame_' + str(format(scans, '03d')) + '.jpg')

    blob = cv2.dnn.blobFromImage(frame, scalefactor=1 / 255, size=(640, 640), mean=[0, 0, 0], swapRB=True, crop=False)

    net.setInput(blob)
    detections = net.forward()[0]

    classes_ids = []
    confidences = []
    car_boxes = []
    rows = detections.shape[0]

    frame_width, frame_height = frame.shape[1], frame.shape[0]
    x_scale = frame_width / 640
    y_scale = frame_height / 640

    for i in range(rows):
        row = detections[i]
        confidence = row[4]
        if confidence > 0.5:  # Use np.any() to check if any element satisfies the condition
            classes_score = row[5:]
            ind = np.argmax(classes_score)
            if classes_score[ind] > 0.5:
                classes_ids.append(ind)
                confidences.append(confidence)
                cx, cy, w, h = row[:4]
                x1 = int((cx - w / 2) * x_scale)
                y1 = int((cy - h / 2) * y_scale)
                width = int(w * x_scale)
                height = int(h * y_scale)
                box = np.array([x1, y1, width, height])
                car_boxes.append(box)

    indices = cv2.dnn.NMSBoxes(car_boxes, confidences, 0.5, 0.5)

    if len(indices) > 0:
        max_iou = 0
        best_car_index = None

        for i, car_box in enumerate(car_boxes):
            if i in indices:
                if classes[classes_ids[i]] == 'car':
                    iou = compute_iou(smoke_boxes, car_box)
                    if iou > max_iou:
                        max_iou = iou
                        best_car_index = i

        if max_iou > 0.1:
            x1, y1, w, h = car_boxes[best_car_index]
            frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (255, 0, 0), 2)
            filename = './frames/smokey_vehicle_detections/frame_' + str(format(scans, '03d')) + '.jpg'
            cv2.imwrite(filename, frame)
            print("Smokey Vehicle Detected")
            platedetection.detectPlate(car_boxes[best_car_index], scans)

    else:
        print("No Smoke Detections")