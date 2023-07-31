import serial as sr
import time

ser = sr.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

data=0
while True:
    try:
        decoded_data = ser.readline().decode()
        data = int(decoded_data)
    except:
        print("Error decoding")
    print('Received data : ', data, ', type : ', type(data))


    