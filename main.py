
import time
import os
import RPi.GPIO as GPIO
import sys
import signal
import requests

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

serial = i2c(port=0, address=0x3C)
device = sh1106(serial)

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((35, 25), "Audiobox", fill="white")

airplayOn = "sudo systemctl start shairport-sync"
airplayOff = "sudo systemctl stop shairport-sync"
wifi = False

def testWifi():
    req = requests.get('http://clients3.google.com/generate_204')
    if req.status_code == 204:
        global wifi
        wifi = True
        print("wifi connected")
        return True
    else:
        wifi = False
        print("no wifi")
        return False

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
    return

mode = "none"

def Airplay():
    GPIO.output(auxRelay,0)
    os.system(airplayOn)
    screen("AirPlay")
    global mode
    mode = "airplay"
    time.sleep(1)
    GPIO.output(airplayRelay,1)
    return

def rca1():
    GPIO.output(airplayRelay,0)
    os.system(airplayOff)
    screen("RCA 1")
    global mode
    mode = "rca1"
    time.sleep(1)
    GPIO.output(rca1Relay,1)
    return

def Aux():
    GPIO.output(rca1Relay,0)
    screen("Aux")
    global mode
    mode = "aux"
    time.sleep(1)
    GPIO.output(auxRelay,1)
    return

def screen(message):
    clearDisp()
    #write what I want
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((35, 25), message, fill="white")
    return

def clearDisp():
    device.clear()
    return

def turnOff():
    screen("Power Off")
    time.sleep(2)
    clearDisp()
#    os.system("sudo shutdown -h now")
    return

powerGPIO = 3 #pin number 5
selectGPIO = 17 #pin number 11

airplayRelay = 13 #33
rca1Relay = 19 #35
auxRelay = 26 #37

def button_callback(channel):
    print(channel)
    if channel == 2:
        #changeSetting()
        if mode == "airplay":
            rca1()
        elif mode == "rca1":
            Aux()
        else:
            testWifi()
            if wifi == True:
                Airplay()
            else:
                rca1()
        print("select button")
    elif channel == 3:
        turnOff()
        print("power button")
        exit
    time.sleep(1)
    return

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM) #GPIO numbers are given as GPIO not pin

	#Setting up button pins as GPIO 17 (pin 11) for power and GPIO 27 (pin 13) as select
    GPIO.setup(powerGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(selectGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(airplayRelay, GPIO.OUT)
    GPIO.setup(rca1Relay, GPIO.OUT)
    GPIO.setup(auxRelay, GPIO.OUT)

#    GPIO.add_event_detect(selectGPIO, GPIO.FALLING, callback=changeSetting, bouncetime = 150)
#    GPIO.add_event_detect(powerGPIO, GPIO.FALLING, callback=turnOff, bouncetime = 250)

    GPIO.add_event_detect(selectGPIO, GPIO.FALLING, callback=lambda x: button_callback(2), bouncetime = 250)
    GPIO.add_event_detect(powerGPIO, GPIO.FALLING, callback=lambda x: button_callback(3), bouncetime = 250)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
    while(True):
        time.sleep(0)
