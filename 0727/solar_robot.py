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
def send_message(sender, receiver, command,data):
    message=dict() # dictionary변수 생성
    #각 key에 value넣기
    message[Message.Sender] = sender
    message[Message.Receiver] = receiver
    message[Message.Command] = command
    message[Message.Data] = data
    json_message = json.dumps(message).encode('utf8')
    team_name.publish("solar", json_message)


# MQTT 브로커에 연결
team_name.connect(broker_address, broker_port, 60)
print('connected')

# solar에 CW전송
# 5초 후
# CCW전송
# 5초 후
# S전송
# 1초 후 
# F전송
send_message('team_name', 'solar', 'CW', None)
print('CW')
time.sleep(1) # 메시지 발송 후 1초 대기
send_message('team_name', 'solar', 'CCW', None)
print('CCW')
time.sleep(1) # 메시지 발송 후 1초 대기
send_message('team_name', 'solar', 'S', None)
print('S')
time.sleep(1) # 메시지 발송 후 1초 대기
send_message('team_name', 'solar', 'F', None)
print('F')
time.sleep(1) # 메시지 발송 후 1초 대기

# F수신되면 종료되게 해보기
'''
while True:
    *mqtt_receive 예제 참고
'''