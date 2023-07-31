import paho.mqtt.client as mqtt
import json
from param import Message, Command
import serial as sr
import time
import threading

#variable
sender = None
receiver = None
command = None
data = None
old_message= None
old_command=None

#Serial Start
ser = sr.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

# MQTT 브로커 정보 설정
broker_address = "192.168.137.158"
broker_port = 1883

# MQTT 클라이언트 객체 생성
wind = mqtt.Client()

# MQTT 브로커에 연결되었을 때 실행되는 콜백 함수
def on_connect(wind, userdata, flags, rc):
    print('connected')
    wind.subscribe("wind")  # 토픽 구독

# MQTT 메시지를 수신했을 때 실행되는 콜백 함수
def on_message(wind, userdata, msg):
    global sender, receiver, command, data, old_message, new_message
    recv = msg.payload.decode() #수신 받은 메세지 변환
    new_message=json.loads(recv)
    receiver = new_message[Message.Receiver]
    if receiver != 'wind':
        pass
    else:
        if new_message == old_message:
            pass
        else:
            sender = new_message[Message.Sender]
            command = new_message[Message.Command]
            old_message = new_message
            print(new_message)
            #print(sender,receiver,command) #각 key의 value 각각 출력

def send_message(command):
    send_message=dict() # dictionary변수 생성
    #각 key에 value넣기
    send_message[Message.Sender] = 'wind' 
    send_message[Message.Receiver] = sender
    send_message[Message.Command] = command
    send_message[Message.Data] = None
    json_message = json.dumps(send_message).encode('utf8')
    wind.publish("wind", json_message)

# MQTT 클라이언트 루프 실행 (수신 대기)
def wind_loop():
    wind.loop_forever()
            

#serial send
def serial_send(command):
    message = command
    msg = message.encode()
    ser.write(msg)
    time.sleep(0.1)

# #serial receive
def serial_receive(old_message):
    try:
        decoded_data = ser.readline().decode()
        if old_message==decoded_data:
            decoded_data=None
        return decoded_data
    except:
        pass
    
# MQTT 클라이언트에 연결 이벤트 콜백 함수 등록
wind.on_connect = on_connect

# MQTT 메시지 수신 이벤트 콜백 함수 등록

wind.on_message = on_message

# MQTT 브로커에 연결
wind.connect(broker_address, broker_port, 60)

#mqtt thread
mqtt_thread = threading.Thread(target=wind_loop)
mqtt_thread.start()

#main loop
while True:
    ser_message=serial_receive(old_message)
    if command == 'R':
        old_command = 'R'
        if old_command == command:
            command = 'A'
        serial_send('R')
    if ser_message=='F\n':
        old_message=serial_receive(old_message)
        command=None
        break
print('Finished Wind_Station run!!')
