import sys, os, random
sys.path.append(os.path.join(sys.path[0], 'Server'))
from evdev import InputDevice, categorize, ecodes
import RPi.GPIO as GPIO
from gpiozero import LED
from Motor import *
from Robotarm import *
from servo import Servo
from Buzzer import Buzzer
from Ultrasonic import *
from threading import Thread
from Thread import *
from ADC import *
from Led import Led
from TailLight import TailLight
from SevenSegDisplay import SevenSegDisplay

# Digital pin values
BUZZERPIN = 17  # Used by Buzzer.py code
LED_PIN = 18  # Used by Led.py code
HEADLIGHTPIN = 16  # Digital PIN connected to the front headlights
RIGHTREDPIN = 20  # Pin used by taillight red
LEFTGREENPIN = 21  # Pin used by left green pin
RIGHTGREENPIN = 21  # Pin used by rightgreen pin (shorted in my implementation
LEFTREDPIN = 26  # pin used by left red pin


# # Dance moves
DLEFT = 101
DRIGHT = 102
DSPIN = 103
DFORWARD = 104
DBACK = 105
DARMUP = 106
DARMDOWN = 107
DCLAP = 108
DTOOT = 109
DSPEED = 1  # speed of each move in seconds

# Bluetooth controller button codes
# button code variables (change to suit your device)
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
updown = 17  # up: -1, down: 1
leftright = 16  # left: -1, right: 1

# Analog axis codes (joystick/back buttons)
leftlr = 0  # 1 left, 127 mid, 255 right
leftud = 1  # 1 up, 127 mid, 255 down
rightlr = 2  # 1 left 127 mid, 255 right
rightud = 5  # 1 up 127 mid 255 down
brake = 10  # 255 max 0 min
gas = 9  # 255 max 0 min

lightstatus = False  # whether headlight is on or off
working = False  # Some movement is triggered already - we do not want to repeatedly 
automode = False  # Automode is initiated
shutdown = False  # Shutdown has been requested


def run_ultrasonic_thread(tabletype=0):
    global automode
    automode = True
    threading.Thread(target=run_ultrasonic, args=(tabletype,)).start()

# Event types
# e=0 - d < x  i.e., obstacle
# e=1 - d >= x i.e., no obstacle
# f=0 - flip_state = False -> LEFT priority
# f=1 - flip_state = True  -> Right Priority
def run_ultrasonic(tabletype=0):
    global automode, display, motor
    # Basic transition table - does not use the random flip
    #           0 forward      1 lookleft     2 lookright    3 goback      4 turnleft     5 turnright   6 flip
    ttable = [[[1,0],[1,0]], [[2,4],[2,4]], [[3,5],[3,5]], [[1,1],[1,1]], [[1,0],[1,0]], [[2,0],[2,0]], [[0,0],[0,0]]]
    
    # Second transition table - always uses the flip to determine where to go
    ttable1 = [[[6,0],[6,0]], [[3,4],[3,4]], [[3,5],[3,5]], [[6,6],[6,6]], [[6,0],[6,0]], [[6,0],[6,0]], [[1,1],[2,2]]]
    
    # Third transition table - uses the previous flip (branch)
    ttable2 = [[[6,0],[6,0]], [[2,4],[3,4]], [[3,5],[1,5]], [[6,6],[6,6]], [[6,6],[6,6]], [[6,6],[6,6]], [[1,1],[2,2]]]

    x = 25 
    ultra = Ultrasonic()
    # Change to a fixed number if needs to repeat
    random.seed()
    print ("Auto drive Start, mode = " + str(tabletype))
    
    cur_state = 0
    flip_state = False
    headlight.on()
    
    while automode:
        if cur_state == 0:
            display.show(1, "FORWARD")
            ultra.look_forward()
            motor.slowforward()
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
            ultra.look_forward()
            motor.backup()
            time.sleep(0.5)
        elif cur_state == 4:
            display.show(1, "TURNLEFT")
            ultra.look_forward()
            motor.turnLeft()
            time.sleep(0.1)
        elif cur_state == 5:
            display.show(1, "TURNRITE")
            ultra.look_forward()
            motor.turnRight()
            time.sleep(0.1)
        elif cur_state == 6:
            display.show(1, "PAUSE")
            ultra.look_forward()
            motor.stopMotor()
            flip_state = (random.random() > 0.5)
            time.sleep(0.25)
        else:
            print "Wrong state?"
            cur_state = 0

        time.sleep(0.1)
        d = ultra.get_distance()
        e = 0 if d < x else 1
        f = 1 if flip_state else 0
        
        if tabletype == 0:
            cur_state = ttable[cur_state][e][f]
        elif tabletype == 1:
            cur_state = ttable1[cur_state][e][f]
        else:
            cur_state = ttable2[cur_state][e][f]
    
    ultra.look_forward()
    headlight.off()
    motor.stopMotor()
    display.show(1, "Auto end")
    print "Auto drive End!"

    def run_dance_thread():
        global automode
        automode = True
        threading.Thread(target=run_dance).start()    

    def dancemove(*args):
        for move in args:
            if not self.automode:
                break
            if move == DLEFT:
                motor.turnLeft()
                time.sleep(DSPEED)
                motor.stopMotor()
            elif move == DRIGHT:
                motor.turnRight()
                time.sleep(DSPEED)
                motor.stopMotor()
            elif move == DSPIN:
                motor.spin()
                time.sleep(DSPEED * 2)
                motor.stopMotor()
            elif move == DFORWARD:
                motor.slowforward()
                time.sleep(DSPEED)
                motor.stopMotor()
            elif move == DBACK:
                motor.slowBackup()
                time.sleep(DSPEED)
                motor.stopMotor()
            elif move == DTOOT:
                self.buzzer.run('1')
                time.sleep(DSPEED / 2)
                self.buzzer.run('0')
                time.sleep(DSPEED / 2)
            elif move == DARMUP:
                self.myservo.setServoPwm(ARM, (ARMSTART + ARMEND) * 2 / 3)
                time.sleep(DSPEED)
            elif move == DARMDOWN:
                self.myservo.setServoPwm(ARM, (ARMSTART + ARMEND) * 1 / 3)
                time.sleep(DSPEED)
            elif move == DCLAP:
                self.myservo.setServoPwm(HAND, HANDEND)
                time.sleep(DSPEED)
                self.myservo.setServoPwm(HAND, HANDSTART)
                time.sleep(DSPEED)
            else:
                print "Invalid dance move?"
            
    def run_dance():
        motor.setMotorModel(0, 0, 0, 0)
        # start light show
        mode = str(random.randint(1, 4))
        ledthread = Thread(target=led.ledMode, args=(mode,))
        ledthread.start()
        while self.automode:
            self.dancemove(DLEFT, DBACK, DFORWARD, DBACK, DARMDOWN, DARMUP, DCLAP, DSPIN, DTOOT, DTOOT,
                           DRIGHT, DBACK, DFORWARD, DBACK, DARMDOWN, DARMUP, DCLAP, DSPIN, DTOOT, DTOOT)
        # self.dancemove(DARMUP, DARMDOWN, DCLAP)
        # stop light show when done
        stop_thread(ledthread)
        self.led.colorWipe(self.led, Color(0, 0, 0), 10)
        display.show(1, "DNCE END")
        print "Dance moves finished"

        
# Get the motor object
motor = Motor()
servo = Servo()
robotarm = Robotarm(servo)
horn = Buzzer()
headlight = LED(HEADLIGHTPIN)        
taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
taillight.bothred()
display = SevenSegDisplay()
led = Led()


# creates object 'gamepad' to store the data
# The device may be different in different boards
# particularly if other input devices are connected

btconnected = False

# Wait for the bt controller to get connected
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

# loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    # print(event)
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            if event.code == aBtn:
                shutdown = False
                if automode:
                    automode = False
                else:
                    display.show(1, "AUTO 0")
                    time.sleep(2)
                    run_ultrasonic_thread()
            elif event.code == bBtn:
                shutdown = False
                if automode:
                    automode = False
                else:
                    display.show(1, "AUTO 1")
                    time.sleep(2)
                    run_ultrasonic_thread(tabletype=1)
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
                if automode:
                    automode = False
                else:
                    display.show(1, "AUTO 2")
                    time.sleep(2)
                    run_ultrasonic_thread(tabletype=2)
            elif event.code == yBtn:
                shutdown = False
                if automode:
                    automode = False
                else:
                    display.show(1, "DANCE")
                    time.sleep(2)
                    run_dance_thread()
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
                motor.setMotorModel(0, 0, 0, 0)
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
                motor.setMotorModel(0, 0, 0, 0)
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
