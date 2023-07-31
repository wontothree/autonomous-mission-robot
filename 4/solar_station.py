import paho.mqtt.client as mqtt
import json
from param import Message, Command
import serial as sr
import time
import threading
from DFRobot_INA219 import INA219

ina219_reading_mA = 1000
ext_meter_reading_mA = 1000

ina = INA219(1, INA219.INA219_I2C_ADDRESS4)                                #Change I2C address by dialing DIP switch

#begin return True if succeed, otherwise return False
while not ina.begin():
    time.sleep(2)
ina.linear_cal(ina219_reading_mA, ext_meter_reading_mA)

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
broker_address = "192.168.0.33"
broker_port = 1883

# MQTT 클라이언트 객체 생성
solar = mqtt.Client()

# MQTT 브로커에 연결되었을 때 실행되는 콜백 함수
def on_connect(solar, userdata, flags, rc):
    print('connected')
    solar.subscribe("solar")  # 토픽 구독 맞는다

# MQTT 메시지를 수신했을 때 실행되는 콜백 함수
def on_message(solar, userdata, msg):
    global sender, receiver, command, data, old_message, new_message
    recv = msg.payload.decode() #수신 받은 메세지 변환
    new_message=json.loads(recv)
    receiver = new_message[Message.Receiver]
    if receiver != 'solar':
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
    send_message[Message.Sender] = 'solar_station' 
    send_message[Message.Receiver] = sender
    send_message[Message.Command] = command
    send_message[Message.Data] = ina.get_power_mW()
    json_message = json.dumps(send_message).encode('utf8')
    solar.publish("solar", json_message)

# MQTT 클라이언트 루프 실행 (수신 대기)
def solar_loop():
    solar.loop_forever()
            

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
        if old_message == decoded_data:
            decoded_data='A'
        return decoded_data
    except:
        pass
    
# MQTT 클라이언트에 연결 이벤트 콜백 함수 등록
solar.on_connect = on_connect

# MQTT 메시지 수신 이벤트 콜백 함수 등록

solar.on_message = on_message

# MQTT 브로커에 연결
solar.connect(broker_address, broker_port, 60)

#mqtt thread
mqtt_thread = threading.Thread(target=solar_loop)
mqtt_thread.start()

#main loop
while True:
    ser_message=serial_receive(old_message)
    print(ser_message)
    if command == 'CW':
        serial_send('C')
    if command == 'CCW':
        serial_send('W')
    if command == 'S':
        serial_send('S') #MOTOR STOP
    if command == 'F':  #stop mqtt for 30 seconds
        old_command='F'
        if old_command == command:
            command = 'A'
        serial_send('F')    #Spike Prime Button(red)        
    if ser_message=='F\n':
        old_message=serial_receive(old_message)
        command=None
print('Finished solar_station run!!')