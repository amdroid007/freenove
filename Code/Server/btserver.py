import sys,os
sys.path.append(os.path.join(sys.path[0],'Server'))
from evdev import InputDevice, categorize, ecodes
from Motor import *
from Robotarm import *
from servo import Servo

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

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    # print(event)
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == aBtn:
                print("A")
            elif event.code == bBtn:
                print("B")
            elif event.code == sBtn:
                print("Start")
            elif event.code == lBtn:
                print("Left Thumb")
            elif event.code == rBtn:
                print("Right Thumb")
            elif event.code == trBtn:
                print("Right back")
                robotarm.tailclose()
            elif event.code == tlBtn:
                print("Left back")
                robotarm.tailopen()
            elif event.code == xBtn:
                print("X")
            elif event.code == yBtn:
                print("Y")
    elif event.type == ecodes.EV_ABS:
        rawvalue = event.value    
        if event.code == updown:
            if event.value == -1:
                robotarm.up()
            elif event.value == 1:
                robotarm.down()
            else:
                robotarm.stop()
        elif event.code == leftright:
            if event.value == -1:
                robotarm.open()
            if event.value == 1:
                robotarm.close()
            else:
                robotarm.stop()
        elif event.code == leftlr:
            if (rawvalue > 122 and rawvalue < 132):
                motor.setMotorModel(0,0,0,0)
                print("Turn completed")
            else:
                speed = int(float(rawvalue - 127) / 127 * 3000)
                print("Left right speed is" + str(speed))
                motor.setMotorModel(speed, speed, -speed, -speed)
        elif event.code == leftud:
            print("Stopping")
            if (rawvalue > 122 and rawvalue < 132):
                motor.setMotorModel(0,0,0,0)
            else:
                speed = int(float(rawvalue - 127) / 127 * 3000)
                print("forward backward speed is" + str(speed))
                motor.setMotorModel(-speed, -speed, -speed, -speed)
        elif event.code == rightud:
            if rawvalue < 50:
                robotarm.front()
            elif rawvalue > 200:
                robotarm.back()
            else:
                robotarm.stop()
        elif event.code == rightlr:
            if rawvalue < 50:
                robotarm.left()
            elif rawvalue > 200:
                robotarm.right()
            else:
                robotarm.stop()
        elif event.code == gas:
            if rawvalue > 100:
                robotarm.tailup()
            else:
                robotarm.stop()
        elif event.code == brake:
            if rawvalue > 100:
                robotarm.taildown()
            else:
                robotarm.stop()
