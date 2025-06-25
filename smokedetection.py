import cv2
import numpy as np
import cardetection
import resources


smoke_model = resources.smoke_model
allowList = '0123456789'
net = cv2.dnn.readNetFromONNX(smoke_model)

def detectSmoke(scans):
    frame = cv2.imread('./frames/frame_video/frame_' + str(format(scans, '03d')) + '.jpg')
    cv2.imshow("Output", frame)
    blob = cv2.dnn.blobFromImage(frame, scalefactor=1 / 255, size=(640, 640), mean=[0, 0, 0], swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward()[0]

    confidences = []
    smoke_boxes = []
    rows = detections.shape[0]

    frame_width, frame_height = frame.shape[1], frame.shape[0]
    x_scale = frame_width / 640
    y_scale = frame_height / 640

    for i in range(rows):
        row = detections[i]
        confidence = row[4]
        if confidence > 0.7    :  # Use np.any() to check if any element satisfies the condition
            classes_score = row[5:]
            ind = np.argmax(classes_score)
            if classes_score[ind] > 0.7:
                confidences.append(confidence)
                cx, cy, w, h = row[:4]
                x1 = int((cx - w / 2) * x_scale)
                y1 = int((cy - h / 2) * y_scale)
                width = int(w * x_scale)
                height = int(h * y_scale)
                box = np.array([x1, y1, width, height])
                smoke_boxes.append(box)

    indices = cv2.dnn.NMSBoxes(smoke_boxes, confidences, 0.5, 0.5)

    for i in indices:
        x1, y1, w, h = smoke_boxes[i]
        img_result = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 0, 255), 2)
        filename = './frames/smoke_detections/frame_' + str(format(scans, '03d')) + '.jpg'
        print("Smoke Detected")
        cv2.imwrite(filename, img_result)
        cardetection.detectCar(smoke_boxes[i], scans)
        break

