import paho.mqtt.client as mqtt
import json
from param import Message
import threading

# MQTT 브로커 정보 설정
broker_address = "192.168.137.158"
broker_port = 1883

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
while True:
    print(sender, receiver, command, data)
    if command == 'F':
        print('Command is Finsh!!')
        break