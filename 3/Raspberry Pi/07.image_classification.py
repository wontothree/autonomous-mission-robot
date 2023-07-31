import time
import numpy as np 
import picamera
from picamera.array import PiRGBArray
import argparse
from PIL import Image
import tflite_runtime.interpreter as tflite
import cv2

camera = picamera.PiCamera()
camera.resolution=(320, 240)
camera.framerate=10
camera.hflip=True
camera.vflip=True
rawCapture=PiRGBArray(camera, size=(320, 240))
time.sleep(0.5)

def load_labels(path):
    with open(path, 'r') as f:
        return {i: line.strip() for i, line in enumerate(f.readlines())}

def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:,:] = image

def classify_image(interpreter, image, top_k=1):
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)
    
    ordered = np.argpartition(-output, top_k)
    return [(i, output[i]) for i in ordered[:top_k]]

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model', help='File path', required=False, default = './model.tflite')
    parser.add_argument('--labels', help='labels path', required=False, default = './labels.txt')
    args = parser.parse_args()
    labels = load_labels(args.labels)
    interpreter = tflite.Interpreter(model_path = args.model)
    interpreter.allocate_tensors()

    for frame in camera.capture_continuous(rawCapture,format='bgr', use_video_port=True):
        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        image = frame.array
        cvtimage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        reimage = cv2.resize(cvtimage,(224,224), Image.ANTIALIAS)
        result = classify_image(interpreter,reimage)
        label_id, prob = result[0]
        print(labels[label_id], prob)
        cv2.putText(image, labels[label_id], (20, 20), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
        cv2.imshow('img',image)
        
        if key == ord('q'):
            break

if __name__ == '__main__':
    main()