import sys,os
sys.path.append(os.path.join(sys.path[0],'Server'))
from evdev import InputDevice, categorize, ecodes
from Motor import *
from Robotarm import *
import RPi.GPIO as GPIO
from servo import Servo
from Buzzer import Buzzer
from Ultrasonic import *
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

lightstatus = False
working = False
automode = False
shutdown = False

def run_ultrasonic_thread():
    global automode
    automode = True
    threading.Thread(target=run_ultrasonic).start()

# Event types
# 0 - d < x
# 1 - d >= x
# 2 - l > r   - for future enhancement not using in first try
# 3 - l <= r  - ditto
def run_ultrasonic():
    global automode, display, motor
    ttable = [[1, 0], [2, 4], [3, 5], [1, 1], [0, 0], [0, 0]]
    x = 25 
    ultra = Ultrasonic()
    print "Auto drive Start!"
    
    cur_state = 0
    
    while automode:
        if cur_state == 0:
            display.show(1, "FORWARD")
            motor.slowforward()
            ultra.look_forward()
        elif cur_state == 1:
            display.show(1, "LOOKLEFT")
            motor.stopMotor()
            ultra.look_left()
        elif cur_state == 2:
            display.show(1, "LOOKRITE")
            motor.stopMotor()
            ultra.look_right()
        elif cur_state == 3:
            display.show(1, "GOBACK")
            motor.backup()
            time.sleep(0.5)
        elif cur_state == 4:
            display.show(1, "TURNLEFT")
            motor.turnLeft()
            time.sleep(0.1)
        elif cur_state == 5:
            display.show(1, "TURNRITE")
            motor.turnRight()
            time.sleep(0.1)
        else:
            print "Wrong state?"
            cur_state = 0

        time.sleep(0.1)
        d = ultra.get_distance()
        e = 0 if d < x else 1
        cur_state = ttable[cur_state][e]
        
    motor.stopMotor()
    display.show(1, "Auto end")
    print "Auto drive End!"
        
# Get the motor object
motor = Motor()
servo = Servo()
robotarm = Robotarm(servo)
horn = Buzzer()
headlight = LED(HEADLIGHTPIN)        
taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
taillight.bothred()
display = SevenSegDisplay()

        

#creates object 'gamepad' to store the data
# The device may be different in different boards
# particularly if other input devices are connected

btconnected = False

while not btconnected:
    try:
        gamepad = InputDevice('/dev/input/event6')
        btconnected = True
    except:
        display.show(1, "ERR-RTRY")
        time.sleep(1)
        display.clear()
        time.sleep(0.5)

display.show(1, "Wall-e Ready!")

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    # print(event)
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == aBtn:
                shutdown = False
                if automode:
                    automode = False
                else:
                    display.show(1, "AUTOMODE")
                    time.sleep(2)
                    run_ultrasonic_thread()
            elif event.code == bBtn:
                shutdown = False
                automode = False
                display.show(1, "B")
            elif event.code == sBtn:
                if shutdown:
                    display.show(1, "Pwr off!")
                    os.system("sudo poweroff")
                else:
                    shutdown = True
                    display.show(1, "Trn off?")
                automode = False
            elif event.code == lBtn:
                shutdown = False
                automode = False
                display.show(1, "Horn")
                horn.run('1')
                time.sleep(0.5)
                horn.run('0')
            elif event.code == rBtn:
                shutdown = False
                automode = False
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
                shutdown = False
                automode = False
                display.show(1, "X")
            elif event.code == yBtn:
                shutdown = False
                automode = False
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
