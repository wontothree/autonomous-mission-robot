import time
import picamera
import cv2
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

    cv2.imshow("image",image)

    if key == ord('q'):
        break


    