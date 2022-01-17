import sys,os
sys.path.append(os.path.join(sys.path[0],'Server'))
from evdev import InputDevice, categorize, ecodes
from Motor import *
from Robotarm import *
import RPi.GPIO as GPIO
from servo import Servo
from Buzzer import Buzzer
from threading import Thread
from Thread import *
from ADC import *
from gpiozero import LED
from TailLight import TailLight
from SevenSegDisplay import SevenSegDisplay

# Digital pin values
BUZZERPIN = 17 # Used by Buzzer.py code
LED_PIN = 18  # Used by Led.py code
HEADLIGHTPIN = 16
RIGHTREDPIN = 20
LEFTGREENPIN = 21
RIGHTGREENPIN = 21
LEFTREDPIN = 26

#creates object 'gamepad' to store the data
# The device may be different in different boards
# particularly if other input devices are connected

gamepad = InputDevice('/dev/input/event6')

#button code variables (change to suit your device)
aBtn = 304
bBtn = 305
xBtn = 307
yBtn = 308
lBtn = 317
rBtn = 318
sBtn = 315
trBtn = 311
tlBtn = 310

# Other button codes - do not exist on my pad
up = 115
down = 114
left = 165
right = 163
playpause = 164

# Digital axis codes (DPad)
updown = 17 # up: -1, down: 1
leftright = 16 # left: -1, right: 1

# Analog axis codes (joystick/back buttons)
leftlr = 0 # 1 left, 127 mid, 255 right
leftud = 1 # 1 up, 127 mid, 255 down
rightlr = 2 # 1 left 127 mid, 255 right
rightud = 5 # 1 up 127 mid 255 down
brake = 10 # 255 max 0 min
gas = 9 # 255 max 0 min

# Get the motor object
motor = Motor()
servo = Servo()
robotarm = Robotarm(servo)
horn = Buzzer()
headlight = LED(HEADLIGHTPIN)        
taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
taillight.bothred()
display = SevenSegDisplay()

lightstatus = False
working = False

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    # print(event)
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == aBtn:
                display.show(1, "A")
            elif event.code == bBtn:
                display.show(1, "B")
            elif event.code == sBtn:
                display.show(1, "Start")
            elif event.code == lBtn:
                display.show(1, "Horn")
                horn.run('1')
                time.sleep(0.5)
                horn.run('0')
            elif event.code == rBtn:
                if lightstatus:
                    display.show(1, "Lite off")
                    headlight.off()
                    lightstatus = False
                else:
                    display.show(1, "Lite on")
                    headlight.on()
                    lightstatus = True
            elif event.code == trBtn:
                display.show(1, "Tail cls")
                robotarm.tailclose()
            elif event.code == tlBtn:
                display.show(1, "Tail opn")
                robotarm.tailopen()
            elif event.code == xBtn:
                display.show(1, "X")
            elif event.code == yBtn:
                display.show(1, "Y")
    elif event.type == ecodes.EV_ABS:
        rawvalue = event.value    
        if event.code == updown:
            if event.value == -1:
                if not working:
                    working = True
                    display.show(1, "Arm up")
                    robotarm.up()
            elif event.value == 1:
                if not working:
                    working = True
                    display.show(1, "Arm down")
                    robotarm.down()
            else:
                working = False
                robotarm.stop()
        elif event.code == leftright:
            if event.value == -1:
                display.show(1, "Claw opn")
                robotarm.open()
            if event.value == 1:
                display.show(1, "Claw cls")
                robotarm.close()
        elif event.code == leftlr:
            if (rawvalue > 122 and rawvalue < 132):
                motor.setMotorModel(0,0,0,0)
                display.show(1, "Stop")
                taillight.bothred()
                working = False
            else:
                speed = int(float(rawvalue - 127) / 127 * 3000)
                if not working:
                    working = True
                    if speed < 0:
                        taillight.rightblink()
                        display.show(1, "Left trn")
                    else:
                        taillight.leftblink()
                        display.show(1, "Rite trn")
                motor.setMotorModel(speed, speed, -speed, -speed)
        elif event.code == leftud:
            if (rawvalue > 122 and rawvalue < 132):
                working = False
                display.show(1, "Stop")
                taillight.bothred()
                motor.setMotorModel(0,0,0,0)
            else:
                speed = int(float(rawvalue - 127) / 127 * 3000)
                if not working:
                    working = True
                    if speed < 0:
                        display.show(1, "Forward")
                    else:
                        display.show(1, "Backward")
                        taillight.flash()
                motor.setMotorModel(-speed, -speed, -speed, -speed)
        elif event.code == rightud:
            if rawvalue < 50:
                if not working:
                    working = True
                    display.show(1, "Arm fwd")
                    robotarm.front()
            elif rawvalue > 200:
                if not working:
                    working = True
                    display.show(1, "Arm back")
                    robotarm.back()
            else:
                working = False
                robotarm.stop()
        elif event.code == rightlr:
            if rawvalue < 50:
                if not working:
                    working = True
                    display.show(1, "Arm left")
                    robotarm.left()
            elif rawvalue > 200:
                if not working:
                    working = True
                    display.show(1, "Arm rite")
                    robotarm.right()
            else:
                working = False
                robotarm.stop()
        elif event.code == gas:
            if rawvalue > 100:
                if not working:
                    working = True
                    display.show(1, "Tail up")
                    robotarm.tailup()
            else:
                working = False
                robotarm.stop()
        elif event.code == brake:
            if rawvalue > 100:
                if not working:
                    working = True
                    display.show(1, "Tail dwn")
                    robotarm.taildown()
            else:
                working = False
                robotarm.stop()
