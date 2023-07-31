import time
import picamera
import cv2
from picamera.array import PiRGBArray
import argparse
from PIL import Image
import tflite_runtime.interpreter as tflite
import numpy as np
import serial as sr
import json
import paho.mqtt.client as mqtt
from param import Message, Command
import threading

#serial start
ser = sr.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

# MQTT 브로커 정보 설정
broker_address = "192.168.0.33"
broker_port = 1883
#topic name
sub_topic1 = 'fw' #from_Wind-Station
sub_topic2 = 'fs'
#variable
phase=0
sender = None
receiver = None
command = None
data = 0
old_message= None
old_command=None

# MQTT 클라이언트 객체 생성
team_name = mqtt.Client()

#send encoded message
def serial_send(decision):
    msg=decision.encode()
    ser.write(msg)
    time.sleep(0.1)

# #serial receive
def serial_receive(old_message):
    try:
        decoded_data = ser.readline().decode()
        if old_message == decoded_data:
            decoded_data='A'
        return decoded_data
    except:
        pass


def make_black(image, threshold = 170):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    black_image=cv2.inRange(gray_image, threshold, 255)
    return black_image, gray_image

def path_decision(image, upper_limit,down_limit):
    height, width = image.shape
    image = image[height-upper_limit:height-down_limit,:]
    height = upper_limit -1
    width = width -1
    image = np.flipud(image)
    
    mask = image!=0
    white_distance = np.where(mask.any(axis=0), mask.argmax(axis=0), height)
    left=0
    right=width
    center=int((left+right)/2)
    left_sum = np.sum(white_distance[left:center-60])
    right_sum = np.sum(white_distance[center+60:right])
    forward_sum = np.sum(white_distance[center-60:center+60])
    print(left_sum, right_sum, forward_sum)

    # 방향 결정
    if forward_sum+left_sum+right_sum > 70500: # 12000 24950
        decision = 'f'
    elif left_sum > right_sum + 350: #1450
        decision = 'l'
    elif left_sum < right_sum + 350:
        decision = 'r'
    elif forward_sum+left_sum+right_sum < 72000 : # 500
        decision = 'b'
    else:
        decision = 's'
    return decision


def on_connect(receive_ex, userdata, flags, rc):
    print('connected')
    team_name.subscribe(sub_topic1)  # wind토픽 구독
    team_name.subscribe(sub_topic2)  # solar토픽 구독

# MQTT 메시지를 수신했을 때 실행되는 콜백 함수
def on_message(receive_ex, userdata, msg):
    global sender, receiver, command, data, message, phase
    try:
        recv = msg.payload.decode() #수신 받은 메세지 변환
        message=json.loads(recv)
        sender = message[Message.Sender]
        receiver = message[Message.Receiver]
        command = message[Message.Command]
        data = message[Message.Data]
    except:
        pass
    if sender == 'wind1' and command == 'A':
        phase=1
    if sender == 'solar1' and command == 'A':
        phase=2
    if command == 'F':
        phase=0

#메세지 딕셔너리
def send_message(sender, receiver, command,data):
    message=dict() # dictionary변수 생성
    #각 key에 value넣기
    message[Message.Sender] = sender 
    message[Message.Receiver] = receiver
    message[Message.Command] = command
    message[Message.Data] = data
    json_message = json.dumps(message).encode('utf8')
    team_name.publish(receiver, json_message)

# MQTT 클라이언트 루프 실행 (수신 대기)
def receive_loop():
    team_name.loop_forever()

# MQTT 클라이언트에 연결 이벤트 콜백 함수 등록
team_name.on_connect = on_connect

# MQTT 메시지 수신 이벤트 콜백 함수 등록
team_name.on_message = on_message

# MQTT 브로커에 연결
team_name.connect(broker_address, broker_port, 60)
print('connected')

#mqtt thread
mqtt_thread = threading.Thread(target=receive_loop)
mqtt_thread.start()

#############################[AI]##############################
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

def AI():
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
        if labels[label_id] == 1:
            serial_send('0 DOG')
        if labels[label_id] == 2:
            serial_send('1 CAT')
        if key == ord('q'):
            break


camera = picamera.PiCamera()
camera.resolution = (320,240)
camera.vflip = True
camera.hflip = True
camera.framerate = 10
rawCapture = PiRGBArray(camera, size =(320,240))
decision = 0
time.sleep(0.05)
down_limit = 70
upper_limit = 240

for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):
    print(phase)
    if phase == 0:
        ser_message= 'h'#serial_receive(old_message)
        if ser_message =='D\n':
            cv2.destroyAllWindows()
            break
        else:    
            key = cv2.waitKey(1) & 0xFF
            image = frame.array
            rawCapture.truncate(0)
            black, gray = make_black(image)
            decision = path_decision(black,upper_limit,down_limit)
            serial_send(decision)
            print(decision)
            cv2.rectangle(image,(0,240-down_limit),(320,240-upper_limit),(0,255,0),3)
            cv2.putText(image, decision, (20, 20), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
            cv2.imshow("image", image)
            cv2.imshow("black",black)

            if key == ord('q'):
                break
    if phase == 1:
        serial_send('s')
        time.sleep(0.7)
        send_message('chamcham', 'wind1' , 'R', None)
        rawCapture.truncate(0)
        time.sleep(0.7)
        phase = 0
    if phase == 2:
        serial_send('s')
        while True:
            send_message('chamcham', 'solar1', 'CW', data)
            mw=data
            print('mw : ', mw)
            time.sleep(0.2)
            print('data : ', data)
            if mw>data:
                while mw!=data:
                    send_message('chamcham', 'solar1', 'CCW', data)
                send_message('chamcham', 'solar1', 'S', data)
                time.sleep(1)
                send_message('chamcham', 'solar1', 'F',data)
                print('The maximum power = ', mw)
                break
        rawCapture.truncate(0)
        phase = 0
#After ultrasensor detect object
AI()
#send to spike last move
#go to line 185