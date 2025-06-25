import cv2
import os
import time
import shutil

import platedetection
import resources
import data
import smokedetection
from datetime import datetime

if not os.path.exists('frames'):
    os.makedirs('frames')

if os.path.exists('frames/frame_cache'):
    shutil.rmtree('./frames/frame_cache')
elif not os.path.exists('frames/frame_cache'):
    os.makedirs('frames/frame_cache')

if not os.path.exists('frames/frame_cache'):
    os.makedirs('frames/frame_cache')

if not os.path.exists('frames/frame_video'):
    os.makedirs('frames/frame_video')

if not os.path.exists('frames/smoke_detections'):
    os.makedirs('frames/smoke_detections')

if not os.path.exists('frames/smokey_vehicle_detections'):
    os.makedirs('frames/smokey_vehicle_detections')

if not os.path.exists('frames/plate_detections'):
    os.makedirs('frames/plate_detections')

if not os.path.isfile('resources/data.py'):
    data.new_json()

cam = resources.cam

totalFrames = len(os.listdir('./frames/frame_video'))
sleep = 1/24

print("Program Initialized")

while True:
    now = datetime.now()
    dtime = now.strftime("%H:%M:%S")
    ddate = now.strftime("%d/%m/%Y")
    ret, img = cam.read()

    sequence = totalFrames + 1
    cv2.imwrite(f'./frames/frame_cache/frame_{sequence:03d}.jpg', img)
    img_txt = cv2.putText(img, f"{dtime} {ddate}", (420, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.imwrite(f'./frames/frame_video/frame_{totalFrames:03d}.jpg', img_txt)
    cv2.imshow('Output', img_txt)
    smokedetection.detectSmoke(totalFrames)

    totalFrames += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(sleep)

cv2.destroyAllWindows()
