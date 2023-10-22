import usocket as socket
import network
from utime import sleep
import re
from machine import Pin
from servo import Servo

led = Pin(25, Pin.OUT)
rp2.country('CA')
ssid = 'ssid here'
password = 'passwrod here'

hpos = 90
vpos = 90
vservo = Servo(pin_id=16)
hservo = Servo(pin_id=15)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip
try:
    ip = connect()
except KeyboardInterrupt:
    machine.reset()

address = (ip, 8080)
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.bind(address)
print(address)
connection.listen(0)
conn, addr = connection.accept()
connection.setblocking(False)
result = [0]
vservo.write(90)
hservo.write(90)
try:
    while True:
        FIRE = False
        data = conn.recv(6)
        decode = data.decode()
        print(decode)
        led.toggle()
        if decode[0] == 'c':
            FIRE = True
            print("FIRE")
        elif decode[0] == 'v':
            result = decode[1:]
            horizontal_angle = float(result)
            print(horizontal_angle)
            hpos = hpos + horizontal_angle/5
            if hpos < 200:
                hservo.write(hpos)
        elif decode[0] == 'h':
            result = decode[1:]
            vertical_angle = float(result)
            print(vertical_angle)
            vpos = vpos + vertical_angle/5
            if vpos < 200:
                vservo.write(vpos)
except KeyboardInterrupt:
    connection.close()
    machine.reset()

