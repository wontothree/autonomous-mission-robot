import time
import picamera
import cv2
import numpy as np
from picamera.array import PiRGBArray

camera = picamera.PiCamera()
camera.resolution=(320,240)
camera.framerate = 10
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(320,240))
time.sleep(0.05)

for frame in camera.capture_continuous(rawCapture,format="bgr",use_video_port=True):
    key = cv2.waitKey(1) & 0xFF
    image = frame.array
    rawCapture.truncate(0)
    
    print(image)
    cv2.imshow("image",image)

    height, width, channel = image.shape
    roi = image[50:height-50,60:width-70]
    cv2.imshow("roi", roi)

    flip = np.flipud(image)
    cv2.imshow("flip",flip)

    if key == ord('q'):
        break