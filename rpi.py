import usocket as socket
import network
from utime import sleep
import re
from machine import Pin
from servo import Servo
vservo = Servo(pin_id=16)
hservo = Servo(pin_id=15)
vservo.write(90)
hservo.write(90)

led = Pin(25, Pin.OUT)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('COMTEPR', "00000000")
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
        led.toggle()
    print(wlan.ifconfig())

try:
    connect()
except KeyboardInterrupt:
    machine.reset()

# Create a socket for communication
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 12345))  # Bind to all available network interfaces

result = [0]
while True:
    data, addr = s.recvfrom(1024)
    decode = data.decode()
    led.toggle()
    if decode[0] == 'c':
        FIRE = True
        print("FIRE")
    elif decode[0] == 'h':
        result = decode[1:]
        horizontal_angle = float(result)
        print(horizontal_angle)
        print(position)
        hservo.write(position)
    elif decode[0] == 'v':
        result = decode[1:]
        vertical_angle = float(result)
        print(vertical_angle)
        vservo.write(position)

    
        
    

