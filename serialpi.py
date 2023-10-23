from utime import sleep
import re
from machine import Pin
from servo import Servo
import sys

led = Pin(25, Pin.OUT)
rp2.country('CA')

hpos = 90
vpos = 90
hservo = Servo(pin_id=16)
vservo = Servo(pin_id=15)
delay_ms = 0.01
result = [0]
vservo.write(90)
hservo.write(90)
try:
    while True:
        FIRE = False
        data = sys.stdin.buffer.read(6)
        decode = data.decode()
        led.toggle()
        if decode[0] == 'b':
            vservo.write(90)
            while hpos < 200:  # Step the position forward from 0deg to 180deg
                hpos = hpos+1
                data = sys.stdin.buffer.read(6)
                decode = data.decode()
                if decode[0] != 'b':
                    break
                print(hpos)  # Show the current position in the Shell/Plotter
                hservo.write(hpos)  # Set the Servo to the current position
                sleep(delay_ms)  # Wait for the servo to make the movement
            while hpos > 1:  # Step the position reverse from 180deg to 0deg
                hpos = hpos-1
                data = sys.stdin.buffer.read(6)
                decode = data.decode()
                if decode[0] != 'b':
                    break
                print(hpos)  # Show the current position in the Shell/Plotter
                hservo.write(hpos)  # Set the Servo to the current position
                sleep(delay_ms)  # Wait for the servo to make the movement
        elif decode[0] == 'c':
            FIRE = True
            print("FIRE")
        elif decode[0] == 'h':
            result = decode[1:]
            horizontal_angle = float(result)
            print(horizontal_angle)
            hpos = hpos + horizontal_angle/5
            if hpos < 200:
                hservo.write(hpos)
        elif decode[0] == 'v':
            result = decode[1:]
            vertical_angle = float(result)
            print(vertical_angle)
            vpos = vpos + vertical_angle/5
            if vpos < 200:
                vservo.write(vpos)
except KeyboardInterrupt:
    connection.close()
    machine.reset()