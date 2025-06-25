import cv2
import numpy as np
import easyocr
import resources
import data

plate_model = resources.plate_model
allowList = '0123456789'
net = cv2.dnn.readNetFromONNX(plate_model)


def detectPlate(car_boxes, scans):

    frame = cv2.imread('./frames/smokey_vehicle_detections/frame_' + str(format(scans, '03d')) + '.jpg')

    clean_frame = cv2.imread('./frames/frame_video/frame_' + str(format(scans, '03d')) + '.jpg')

    car_x, car_y, car_w, car_h = car_boxes

    cropped_car = clean_frame[car_y:car_y + car_h, car_x:car_x + car_w]

    blob = cv2.dnn.blobFromImage(cropped_car, scalefactor=1 / 255, size=(640, 640), mean=[0, 0, 0], swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward()[0]

    confidences = []
    boxes = []
    rows = detections.shape[0]

    frame_width, frame_height = cropped_car.shape[1], cropped_car.shape[0]
    x_scale = frame_width / 640
    y_scale = frame_height / 640

    for i in range(rows):
        row = detections[i]
        confidence = row[4]
        if confidence > 0.5:  # Use np.any() to check if any element satisfies the condition
            classes_score = row[5:]
            ind = np.argmax(classes_score)
            if classes_score[ind] > 0.5:
                confidences.append(confidence)
                cx, cy, w, h = row[:4]
                x1 = int((cx - w / 2) * x_scale)
                y1 = int((cy - h / 2) * y_scale)
                width = int(w * x_scale)
                height = int(h * y_scale)
                box = np.array([x1, y1, width, height])
                boxes.append(box)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.5)

    if len(indices) > 0:
        for i in indices:
            x1, y1, w, h = boxes[i]
            area = w * h

            if area > 0:
                cv2.rectangle(frame, (car_x + x1, car_y + y1), (car_x + x1 + w, car_y + y1 + h), (0, 255, 0), 2)
                cropped_plate = cropped_car[y1:y1 + h, x1:x1 + w]

                reader = easyocr.Reader(['en'])
                result = reader.readtext(cropped_plate, allowlist=allowList, min_size=0, mag_ratio=3)

                for a in range(0, len(result)):
                    if result[a][2] >= 0.5 and len(str(result[a][1])) >= 4:
                        plate = str(result[a][1])
                        conf = str(format(result[a][2], '.2%'))
                        filename = './frames/plate_detections/frame_' + str(format(scans, '03d')) + '.jpg'
                        text_result = (plate + ", " + conf)

                        img_result = cv2.putText(frame, text_result, (car_x + x1, car_y + y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        print(text_result)
                        cv2.imshow(str(result[a][1]), img_result)
                        cv2.imwrite(filename, img_result)
                        data.write_violation(plate, conf, filename)

                        break
                    else:
                        print("Plate Detected Failed Result: " + str(format(result[a][2], '.2%')))
                        break
    else:
        print("No Plate Detections")
