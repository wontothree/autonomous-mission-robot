import paho.mqtt.client as mqtt
import json
from param import Message, Command
import serial as sr
import time
import threading
from DFRobot_INA219 import INA219

ina219_reading_mA = 1000
ext_meter_reading_mA = 1000

ina = INA219(1, INA219.INA219_I2C_ADDRESS4)                                
#begin return True if succeed, otherwise return False
while not ina.begin():
    time.sleep(2)
ina.linear_cal(ina219_reading_mA, ext_meter_reading_mA)

#variable
sender = None
receiver = None
command = None
data = 0
old_message= None
old_command=None
sub_topic='solar2'  #station name
pub_topic='fs'  #from solar

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
    solar.subscribe(sub_topic)  # 토픽 구독

# MQTT 메시지를 수신했을 때 실행되는 콜백 함수
def on_message(solar, userdata, msg):
    global sender, receiver, command, data, old_message, new_message
    recv = msg.payload.decode() #수신 받은 메세지 변환
    new_message=json.loads(recv)
    receiver = new_message[Message.Receiver]
    if receiver != 'solar2':
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

def send_message(s_sender,s_receiver,s_command,s_data):
    send_message=dict() # dictionary변수 생성
    #각 key에 value넣기
    send_message[Message.Sender] = s_sender
    send_message[Message.Receiver] = s_receiver
    send_message[Message.Command] = s_command
    send_message[Message.Data] = s_data
    json_message = json.dumps(send_message).encode('utf8')
    solar.publish(pub_topic, json_message)
    print(json_message)
         
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
solar.on_message = on_message
solar.connect(broker_address, broker_port, 60) # MQTT 브로커에 연결
# MQTT 클라이언트 루프 실행 (수신 대기)
def solar_loop():
    solar.loop_forever()
#mqtt thread
mqtt_thread = threading.Thread(target=solar_loop)
mqtt_thread.start()

#main loop
while True:
    phase = 0
    ser_message=serial_receive(old_message)
    if ser_message == 'D\n': #UltraSensor detected
        send_message('solar2','receiver','A',0)
        print('robot_detect')
        t=time.time()
        while True:
            send_message('solar2','receiver','D',ina.get_power_mW())   
            print(phase)
            ser_message=serial_receive(old_message)
            if (time.time()-t>10 and phase==0)or(time.time()-t>30):
                serial_send('F')
                print('time_out')
                break
            else:
                if command=='A':
                    pass
                if command == 'CW':
                    phase=1
                    serial_send('C')
                if command == 'CCW':
                    phase=1
                    serial_send('W')
                if command == 'S':
                    phase=1
                    serial_send('S') #MOTOR STOP
                if command == 'F':  #stop mqtt for 30 seconds
                    old_command='F'
                    serial_send('F')    #Spike Prime Button(red)       
                if ser_message=='F\n':
                    send_message('sender2','receiver','F',None)
                    old_message=serial_receive(old_message)
                    sender = None
                    receiver = None
                    command = None
                    data = None
                    old_message= None
                    old_command=None
                    break    
    
print('Finished solar_station run!!')
