import time
import picamera
import cv2
from picamera.array import PiRGBArray

def make_black(image, threshold = 140):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    black_image=cv2.inRange(gray_image, threshold, 255)
    return black_image, gray_image

camera = picamera.PiCamera()
camera.resolution = (320, 240)
camera.framerate = 10
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(320, 240))
time.sleep(0.05)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    key = cv2.waitKey(1) & 0xFF
    image = frame.array
    rawCapture.truncate(0)
    
    black , gray = make_black(image)
    cv2.imshow("color", image)
    cv2.imshow("gray", gray)
    cv2.imshow("black", black)
    
    if key == ord('q'):
        break
