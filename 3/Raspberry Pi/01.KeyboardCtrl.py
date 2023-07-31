import pygame 
import serial as sr
import time                        

pygame.init()                                   #pygame initialize
pygame.display.set_caption("Keyboard Control")  #window name
screen = pygame.display.set_mode((200,200))     #window size
screen.fill((0, 0, 0))                          #fill the screen with black

#serial start
ser = sr.Serial('/dev/ttyS0', baudrate=9600, timeout=1)

#send encoded message
def serial_send(key):
    msg=key.encode()
    ser.write(msg)
    time.sleep(0.1)


try:
    exit=False
    while not exit:
        for event in pygame.event.get():        #key값 받기
            pressed = pygame.key.get_pressed()  #눌린 key
            key="s"
            if pressed[pygame.K_q]:
                exit = True
            if pressed[pygame.K_UP]:
                key="f"
            elif pressed[pygame.K_DOWN]:
                key="b"
            elif pressed[pygame.K_LEFT]:
                key="l"
            elif pressed[pygame.K_RIGHT]:
                key="r"
        serial_send(key)
finally:
    print("Control End")

