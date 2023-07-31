import serial as sr
import time

#Serial Start
ser = sr.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

while True:
    message = 'r'
    msg = message.encode()
    ser.write(msg)
    time.sleep(0.1)


    