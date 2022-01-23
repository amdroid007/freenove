import io
import os
import socket
import struct
import time
import threading
import picamera
import sys, getopt
import random
import RPi.GPIO as GPIO
from threading import Thread
from Thread import *
from server import Server
from evdev import InputDevice, categorize, ecodes
from rpi_ws281x import *
from select import select
from Motor import *
from Buzzer import *
from Ultrasonic import *
from ADC import *
from servo import *
from Robotarm import Robotarm
from gpiozero import LED
from Led import Led
from TailLight import TailLight
from SevenSegDisplay import SevenSegDisplay

# Rear arm channels
ARM = '2'
HAND = '3'

# special keys
ESCAPE = 1
OK = 28

# movement and function keys
THROW = 20  # T
STARTAUTO = 22  # U
STARTLINE = 23  # I
STARTLANE = 30  # A
SHAKE = 16  # Q = shaq?
DANCE = 32  # D
HIFIVE = 35  # H
STARTLIGHT = 24  # O = optical

ARMUP = 31  # S = 31
ARMDOWN = 45  # X = 45
REACHFORWARD = 38  # L = 38
REACHBACK = 52  # . = 52
CLAWOPEN = 44  # Z = 44
CLAWCLOSE = 46  # C = 46
ARMLEFT = 51  # , = 51
ARMRIGHT = 39  # ; = 39?

# Additional special keys
SPACE = 57
UP = 103
LEFT = 105
RIGHT = 106
DOWN = 108
VDOWN = 114
VUP = 115
NEXT = 163
PLAY = 164
PREV = 165
CONFIG = 171

# Rear arm values
ARMSTART = 150 
ARMEND = 35
SHAKESTART = 130
SHAKE2 = 120
SHAKE1 = 110
SHAKEEND = 100
HIFIVEEND = 130
HANDSTART = 25 
HANDEND = 120

# Digital pin values
BUZZERPIN = 17  # Used by Buzzer.py code
LED_PIN = 18  # Used by Led.py code
HEADLIGHTPIN = 16
RIGHTREDPIN = 20
LEFTGREENPIN = 21
RIGHTGREENPIN = 21
LEFTREDPIN = 26

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


class myapp():
    
    def __init__(self, motor=None, headlight=None, taillight=None, buzzer=None, display=None):
        self.PWM = motor
        self.serverup = False
        self.automode = False
        self.taillight = taillight
        self.TCP_Server = Server(motor, headlight, taillight, buzzer)
        self.adc = Adc()
        self.led = Led()
        self.buzzer = buzzer
        self.myservo = Servo()
        self.robotarm = Robotarm(self.myservo)
        self.display = display
        print "Initializing..."
        self.on_pushButton()
                        
    def close(self):
        print "Closing down..."
        try:
           stop_thread(self.SendVideo)
           stop_thread(self.ReadData)
           stop_thread(self.power)
           self.robotarm.stop()
        except:
            pass
        try:
            self.TCP_Server.server_socket.shutdown(2)
            self.TCP_Server.server_socket1.shutdown(2)
            self.TCP_Server.StopTcpServer()
        except:
            pass
        self.serverup = False
        print "Close TCP" 
        os._exit(0)
    
    def on_pushButton(self):
        if self.serverup == False:
            self.TCP_Server.tcp_Flag = True
            print "Open TCP"
            self.TCP_Server.StartTcpServer()
            self.SendVideo = Thread(target=self.TCP_Server.sendvideo)
            self.ReadData = Thread(target=self.TCP_Server.readdata)
            self.power = Thread(target=self.TCP_Server.Power)
            self.SendVideo.start()
            self.ReadData.start()
            self.power.start()
            self.serverup = True
            
        elif self.serverup == True:
            self.TCP_Server.tcp_Flag = False
            try:
                stop_thread(self.ReadData)
                stop_thread(self.power)
                stop_thread(self.SendVideo)
            except:
                pass
            
            self.TCP_Server.StopTcpServer()
            self.serverup = False
            print "Close TCP"
 
    def run_light_thread(self):
        self.automode = True
        threading.Thread(target=self.run_light).start()
            
    def run_line_thread(self):
        self.automode = True
        threading.Thread(target=self.run_line).start()
        
    def run_ultrasonic_thread(self):
        self.automode = True
        threading.Thread(target=self.run_ultrasonic).start()
        
    def run_dance_thread(self):
        self.automode = True
        threading.Thread(target=self.run_dance).start()    
    
    def run_lane_thread(self):
        self.automode = True
        threading.Thread(target=self.run_lane).start()
        
    # Event types
    # 0 - d < x
    # 1 - d >= x
    # 2 - l > r   - for future enhancement not using in first try
    # 3 - l <= r  - ditto
    def run_ultrasonic(self):
        IR01 = 14
        IR02 = 15
        IR03 = 23
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IR01, GPIO.IN)
        GPIO.setup(IR02, GPIO.IN)
        GPIO.setup(IR03, GPIO.IN)
        self.LMR0 = 0x00
        if GPIO.input(IR01) == False:
            self.LMR0 = (self.LMR0 | 4)
        if GPIO.input(IR02) == False:
            self.LMR0 = (self.LMR0 | 2)
        if GPIO.input(IR03) == False:
            self.LMR0 = (self.LMR0 | 1)

	if self.LMR0 > 0:
	    self.LMR0 = 7
        ttable = [[1, 0], [2, 4], [3, 5], [1, 1], [0, 0], [0, 0]]
        x = 40
        ultra = Ultrasonic()
        print "Auto drive Start!"
        
        cur_state = 0
        
        while self.automode:
            if cur_state == 0:
                self.display.show(1, "FORWARD")
                self.PWM.slowforward()
                ultra.look_forward()
            elif cur_state == 1:
                self.display.show(1, "LOOKLEFT")
                self.PWM.stopMotor()
                ultra.look_left()
		time.sleep(0.2)
            elif cur_state == 2:
                self.display.show(1, "LOOKRITE")
                self.PWM.stopMotor()
                ultra.look_right()
		time.sleep(0.2)
            elif cur_state == 3:
                self.display.show(1, "GOBACK")
                self.PWM.backup()
            elif cur_state == 4:
                self.display.show(1, "TURNLEFT")
                self.PWM.turnLeft()
                time.sleep(0.2)
            elif cur_state == 5:
                self.display.show(1, "TURNRITE")
                self.PWM.turnRight()
                time.sleep(0.2)
            else:
                print "Wrong state?"
                cur_state = 0

            time.sleep(0.1)
            d = ultra.get_distance()
            self.LMR = 0x00
            if GPIO.input(IR01) == False:
                self.LMR = (self.LMR | 4)
            if GPIO.input(IR02) == False:
                self.LMR = (self.LMR | 2)
            if GPIO.input(IR03) == False:
                self.LMR = (self.LMR | 1)
            if (False and self.LMR <> self.LMR0):  # disabling this temporarily
                cur_state = 3
	    else:
                e = 0 if d < x else 1
                cur_state = ttable[cur_state][e]
            
        print "Auto drive End!"
            
    # Event types
    # 0 - d < x
    # 1 - d >= x
    # 2 - l > r   - for future enhancement not using in first try
    # 3 - l <= r  - ditto
    def run_lane(self):
        IR01 = 14
        IR02 = 15
        IR03 = 23
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IR01, GPIO.IN)
        GPIO.setup(IR02, GPIO.IN)
        GPIO.setup(IR03, GPIO.IN)

        x = 10
        ultra = Ultrasonic()

        ttable = [[0, 3, 1, 2, 1], [0, 3, 1, 2, 2], [0, 3, 1, 2, 1], [0, 0, 0, 0, 0]]
        
        print "Lane keep start!"
        
        cur_state = 0
        
        while self.automode:
            if cur_state == 0:
                self.display.show(1, "FORWARD")
                self.PWM.slowforward()
                ultra.look_forward()
            elif cur_state == 1:
                self.display.show(1, "TURNLEFT")
                self.PWM.setMotorModel(-1500, -1500, 1500, 1500)
            elif cur_state == 2:
                self.display.show(1, "TURNRITE")
                self.PWM.setMotorModel(1500, 1500, -1500, -1500)
            else:
                self.display.show(1, "WALL!")
                self.PWM.setMotorModel(0, 0, 0, 0)
                self.automode = False

            time.sleep(0.1)
            d = ultra.get_distance()
            self.LMR = 0x00
            if GPIO.input(IR01) == False:
                self.LMR = (self.LMR | 4)
            if GPIO.input(IR02) == False:
                self.LMR = (self.LMR | 2)
            if GPIO.input(IR03) == False:
                self.LMR = (self.LMR | 1)

            e = 0
            
            if d < x:
                e = 1
            elif self.LMR == 4 or self.LMR == 6:
                e = 3
            elif self.LMR == 1 or self.LMR == 3:
                e = 2
            elif self.LMR == 2:
                e = 4
            
            cur_state = ttable[cur_state][e]
            print("LMR: " + str(self.LMR) + " Cur state: " + str(cur_state))
            
        print "Lane keep End!"
            
    def run_line(self):
        IR01 = 14
        IR02 = 15
        IR03 = 23
        print "Line Follow Start!"
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IR01, GPIO.IN)
        GPIO.setup(IR02, GPIO.IN)
        GPIO.setup(IR03, GPIO.IN)
        while self.automode:
            self.LMR = 0x00
            if GPIO.input(IR01) == False:
                self.LMR = (self.LMR | 4)
            if GPIO.input(IR02) == False:
                self.LMR = (self.LMR | 2)
            if GPIO.input(IR03) == False:
                self.LMR = (self.LMR | 1)
            if self.LMR == 2:
                self.display.show(1, "FORWARD")
                self.PWM.setMotorModel(800, 800, 800, 800)
            elif self.LMR == 4:
                self.display.show(1, "TURNLEFT")
                self.PWM.setMotorModel(-1000, -1000, 1500, 1500)
            elif self.LMR == 3:
                self.display.show(1, "FASTLEFT")
                self.PWM.setMotorModel(-1500, -1500, 2000, 2000)
            elif self.LMR == 1:
                self.display.show(1, "TURNRIGHT")
                self.PWM.setMotorModel(1500, 1500, -1000, -1000)
            elif self.LMR == 6:
                self.display.show(1, "FASTRITE")
                self.PWM.setMotorModel(2000, 2000, -1500, -1500)
            elif self.LMR == 7:
                pass
        print "Line Follow End!"
            
    def run_light(self):
        print "Light follow start!"
        self.PWM.setMotorModel(0, 0, 0, 0)
        while self.automode:
            L = self.adc.recvADC(0)
            R = self.adc.recvADC(1)
            if L < 2.99 and R < 2.99:
                self.display.show(1, "FORWARD")
                self.PWM.setMotorModel(1000, 1000, 1000, 1000)
                
            elif abs(L - R) < 0.15:
                self.display.show(1, "STOP")
                self.PWM.setMotorModel(0, 0, 0, 0)
                
            elif L > 3 or R > 3:
                if L > R:
                    self.display.show(1, "TURNLEFT")
                    self.PWM.setMotorModel(-1500, -1500, 2000, 2000)
                    
                elif R > L:
                    self.display.show(1, "TURNRITE")
                    self.PWM.setMotorModel(2000, 2000, -1500, -1500)
        print "Light follow finished!"
    
    def dancemove(self, *args):
        for move in args:
    	    if not self.automode:
                break
            if move == DLEFT:
                self.PWM.turnLeft()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DRIGHT:
                self.PWM.turnRight()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DSPIN:
                self.PWM.spin()
                time.sleep(DSPEED * 2)
                self.PWM.stopMotor()
            elif move == DFORWARD:
                self.PWM.slowforward()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
            elif move == DBACK:
                self.PWM.slowBackup()
                time.sleep(DSPEED)
                self.PWM.stopMotor()
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
            
    def run_dance(self):
        print "Dance moves"
        self.PWM.setMotorModel(0, 0, 0, 0)
        # start light show
        mode = str(random.randint(1, 4))
        ledthread = Thread(target=self.led.ledMode, args=(mode,))
        ledthread.start()
        while self.automode:
            self.dancemove(DLEFT, DBACK, DFORWARD, DBACK, DARMDOWN, DARMUP, DCLAP, DSPIN, DTOOT, DTOOT,
                           DRIGHT, DBACK, DFORWARD, DBACK, DARMDOWN, DARMUP, DCLAP, DSPIN, DTOOT, DTOOT)
	    # self.dancemove(DARMUP, DARMDOWN, DCLAP)
        # stop light show when done
        stop_thread(ledthread)

	self.led.colorWipe(self.led, Color(0, 0, 0), 10)
        print "Dance moves finished"


if __name__ == '__main__':
    devices = map(InputDevice, ('/dev/input/event0', '/dev/input/event3'))
    devices = {dev.fd: dev for dev in devices}
    for dev in devices.values(): 
         print(dev)
    buzzer = Buzzer()
    curarmangle = ARMSTART
    curhandangle = HANDSTART
    headlight = LED(HEADLIGHTPIN)
    taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
    display = SevenSegDisplay()
    
    PWM = Motor(taillight)
    myshow = myapp(PWM, headlight, taillight, buzzer, display)
    display.show(0, "WELCOME MSIS STUDENTS")
    
    myshow.myservo.setServoPwm(ARM, curarmangle)
    myshow.myservo.setServoPwm(HAND, curhandangle)
    sdcount = 0
    try:
        while True:
           r, w, x = select(devices, [], [])
           for fd in r:
              for event in devices[fd].read():
                if event.type == ecodes.EV_KEY:
                    if event.value == 0:  # release stop
                        if event.code != 57:
                            if PWM.moving and not(myshow.automode):
                                PWM.stopMotor()  # This will turn on the taillight
                            	display.show(1, "Stop")
                            myshow.robotarm.stop()
                            buzzer.run('0')
                            sdcount = 0
                    elif event.value == 1:  # press - start
                        if event.code == UP:
                            PWM.forward()
                            display.show(1, "Forward")
                        elif event.code == DOWN:
                            PWM.backup()
                            display.show(1, "Backward")
                        elif event.code == LEFT:
                            PWM.turnLeft()
                            display.show(1, "LEFT")
                        elif event.code == RIGHT:
                            PWM.turnRight()
                            display.show(1, "RIGHT")
                        elif event.code == SPACE:
                            myshow.on_pushButton()
                            display.show(1, "Server start-stop")
                        elif event.code == OK:
                            buzzer.run('1') 
                            display.show(1, "Horn!")
                        elif event.code == ARMLEFT:
                            myshow.robotarm.left() 
                            display.show(1, "ARM LEFT")
                        elif event.code == ARMRIGHT:
                            myshow.robotarm.right() 
                            display.show(1, "ARM RITE")
                        elif event.code == CLAWOPEN:
                            myshow.robotarm.open() 
                            display.show(1, "CLAW OPN")
                        elif event.code == CLAWCLOSE:
                            myshow.robotarm.close() 
                            display.show(1, "CLAW CLS")
                        elif event.code == ARMUP:
                            myshow.robotarm.up() 
                            display.show(1, "ARM UP")
                        elif event.code == ARMDOWN:
                            myshow.robotarm.down() 
                            display.show(1, "ARM DOWN")
                        elif event.code == REACHBACK:
                            myshow.robotarm.back() 
                            display.show(1, "ARM BACK")
                        elif event.code == REACHFORWARD:
                            myshow.robotarm.front() 
                            display.show(1, "ARM FWD")
                        elif event.code == VUP:
                            display.show(1, "Arm up")
                            if curarmangle <= ARMSTART - 5:
                                curarmangle = curarmangle + 5
                                myshow.myservo.setServoPwm(ARM, curarmangle)
                        elif event.code == VDOWN:
                            display.show(1, "Arm down")
                            if curarmangle >= ARMEND + 5:
                                curarmangle = curarmangle - 5
                                myshow.myservo.setServoPwm(ARM, curarmangle)
                        elif event.code == THROW:
                            display.show(1, "Throw")
                            curarmangle = ARMSTART
                            myshow.myservo.setServoPwm(ARM, curarmangle)
                            time.sleep(0.1)
                            myshow.myservo.setServoPwm(HAND, HANDSTART)
                        elif event.code == HIFIVE:
                            display.show(1, "Highfive")
                            curangle = HIFIVEEND
                            myshow.myservo.setServoPwm(HAND, HANDSTART)
                            myshow.myservo.setServoPwm(ARM, ARMSTART)
                            time.sleep(2)
                            myshow.myservo.setServoPwm(ARM, HIFIVEEND)
                        elif event.code == SHAKE:
                            display.show(1, "Shake")
                            curangle = SHAKESTART
                            myshow.myservo.setServoPwm(ARM, curarmangle)
                            myshow.myservo.setServoPwm(HAND, HANDSTART)
                            time.sleep(1)
                            myshow.myservo.setServoPwm(HAND, HANDEND)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE2)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE1)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKEEND)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE1)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE2)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKESTART)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE2)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE1)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKEEND)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE1)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKE2)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(ARM, SHAKESTART)
                            time.sleep(0.5)
                            myshow.myservo.setServoPwm(HAND, HANDSTART)
                        elif event.code == PLAY:
                            display.show(1, "Arm rest")
                            curarmangle = (ARMSTART + ARMEND) / 2
                            myshow.myservo.setServoPwm(ARM, curarmangle)
                        elif event.code == PREV:
                            display.show(1, "OPEN")
                            myshow.myservo.setServoPwm(HAND, HANDSTART)
                        elif event.code == NEXT:
                            display.show(1, "CLOSE")
                            myshow.myservo.setServoPwm(HAND, HANDEND)
                        elif event.code == CONFIG:
                            display.show(1, "LIGHT on-off")
                            headlight.toggle()
                        elif event.code == ESCAPE:
                            display.show(1, "AUTO END")
                            myshow.automode = False
                        elif event.code == STARTAUTO:
                            display.show(1, "AUTOMODE")
                            time.sleep(3)
                            myshow.run_ultrasonic_thread()
                        elif event.code == STARTLINE:
                            display.show(1, "PATHMODE")
                            time.sleep(3)
                            myshow.run_line_thread()
                        elif event.code == STARTLIGHT:
                            display.show(1, "LITEMODE")
                            time.sleep(3)
                            myshow.run_light_thread()
                        elif event.code == STARTLANE:
                            display.show(1, "LANEMODE")
                            time.sleep(3)
                            myshow.run_lane_thread()
                        elif event.code == DANCE:
                            display.show(1, "DANCE")
                            myshow.run_dance_thread()
                        else:
                            display.show(1, "UNKNOWN KEY")
                            print(categorize(event))
                    elif event.value == 2:  # Holding - long press processing
                        if event.code == 57:  # long press play/pause button
                            sdcount = sdcount + 1
    		if sdcount > 30:
                    display.show(1, "POWER OFF")
                    os.system("sudo poweroff")
    except KeyboardInterrupt:
        myshow.close()
