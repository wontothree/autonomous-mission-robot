import time
import json
import paho.mqtt.client as mqtt
from param import Message, Command

# MQTT 브로커 정보 설정
broker_address = "192.168.0.33"
broker_port = 1883

# MQTT 클라이언트 객체 생성
team_name = mqtt.Client()

#메세지 딕셔너리
def send_message(sender, receiver, command, data):
    message=dict() # dictionary변수 생성
    #각 key에 value넣기
    message[Message.Sender] = sender 
    message[Message.Receiver] = receiver
    message[Message.Command] = command
    message[Message.Data] = data
    json_message = json.dumps(message).encode('utf8')
    team_name.publish("wind", json_message)


# MQTT 브로커에 연결
team_name.connect(broker_address, broker_port, 60)
print('connected')

# wind에 R전송
# 5초 후
# wind에 F전송
# send_message('wony', 'wind', 'R', None)
# print('R')
# time.sleep(1) # 메시지 발송 후 1초 대기
# send_message('wony', 'wind', 'F', None)
# print('F')
# time.sleep(1) # 메시지 발송 후 1초 대기

# F수신되면 종료되게 해보기
'''
while True:
    *mqtt_receive 예제 참고
'''

#########################

import paho.mqtt.client as mqtt
import json
from param import Message
import threading

#variable
sender = None
receiver = None
command = None
data = None
old_message= None
old_command=None

# MQTT 클라이언트 객체 생성
receive_ex = mqtt.Client()

# MQTT 브로커에 연결되었을 때 실행되는 콜백 함수
def on_connect(receive_ex, userdata, flags, rc):
    print('connected')
    receive_ex.subscribe("solar")  # 토픽 구독

# MQTT 메시지를 수신했을 때 실행되는 콜백 함수
def on_message(receive_ex, userdata, msg):
    global sender, receiver, command, data, message
    recv = msg.payload.decode() #수신 받은 메세지 변환
    message=json.loads(recv)
    sender = message[Message.Sender]
    receiver = message[Message.Receiver]
    command = message[Message.Command]
    data = message[Message.Data]

# MQTT 클라이언트에 연결 이벤트 콜백 함수 등록
receive_ex.on_connect = on_connect

# MQTT 메시지 수신 이벤트 콜백 함수 등록
receive_ex.on_message = on_message

# MQTT 브로커에 연결
receive_ex.connect(broker_address, broker_port, 60)

# MQTT 클라이언트 루프 실행 (수신 대기)
def receive_ex_loop():
    receive_ex.loop_forever()

#mqtt thread
mqtt_thread = threading.Thread(target=receive_ex_loop)
mqtt_thread.start()

#특정 value를 확인하면 멈추기
# while True:
#     print(sender, receiver, command, data)
#     if command == 'F':
#         print('Command is Finsh!!')
#         break

# while True:
#     print(sender, receiver, command, data)
    # if receiver == "wony" and sender == "wind" and Command == 'F':
    #     print('Command is Finsh!!')
    #     break


while True:
    send_message("chamchamcham", 'wind', 'R', None)
    print("보냄")
    time.sleep(4)
    print(sender, receiver, command, data)
    if sender == "chamchamcham":
        print("finish")
    if command == 'F':
        print('fff')